#include "routing_engine.hpp"
#include <filesystem>
#include <iostream>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <vector>

// Include the CH library headers
#include "shortcut_graph.hpp"

#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/geometries/box.hpp>
#include <boost/geometry/index/rtree.hpp>
#include <regex>

namespace fs = std::filesystem;

// Define Boost Geometry types for convenience
typedef boost::geometry::model::point<double, 2, boost::geometry::cs::cartesian> Point;
typedef boost::geometry::model::box<Point> Box;
typedef std::pair<Box, uint32_t> Value; // Stores bounding box and edge_id
namespace bgi = boost::geometry::index;

RoutingEngine::RoutingEngine() {}

// Helper to parse WKT LINESTRING
std::vector<std::pair<double, double>> parse_wkt_linestring(const std::string& wkt) {
    std::vector<std::pair<double, double>> points;
    // Simple regex to find coordinate pairs
    // WKT format: LINESTRING (lon lat, lon lat, ...)
    try {
        size_t start = wkt.find('(');
        size_t end = wkt.find(')');
        if (start == std::string::npos || end == std::string::npos) return points;
        
        std::string coords_str = wkt.substr(start + 1, end - start - 1);
        std::stringstream ss(coords_str);
        std::string segment;
        
        while (std::getline(ss, segment, ',')) {
            std::stringstream point_ss(segment);
            double lon, lat;
            if (point_ss >> lon >> lat) {
                points.push_back({lat, lon}); // Store as Lat, Lon for API consistency
            }
        }
    } catch (...) {
        // Ignore parsing errors for robustness
    }
    return points;
}

// Minimal CSV parser handling quotes
std::vector<std::string> parse_csv_line(const std::string& line) {
    std::vector<std::string> result;
    bool in_quotes = false;
    std::string current;
    for (char c : line) {
        if (c == '"') {
            in_quotes = !in_quotes;
        } else if (c == ',' && !in_quotes) {
            result.push_back(current);
            current.clear();
        } else {
            current.push_back(c);
        }
    }
    result.push_back(current);
    return result;
}

bool RoutingEngine::load_dataset(const std::string& dataset_name, const std::string& datasets_path,
                                 const std::string& explicit_shortcuts_path,
                                 const std::string& explicit_edges_path) {
    try {
        std::string shortcuts_path;
        std::string edges_path;

        if (!explicit_shortcuts_path.empty() && !explicit_edges_path.empty()) {
            shortcuts_path = explicit_shortcuts_path;
            edges_path = explicit_edges_path;
        } else {
            std::string dataset_dir = datasets_path + "/" + dataset_name;
            if (!fs::exists(dataset_dir)) {
                std::cerr << "Dataset directory not found: " << dataset_dir << std::endl;
                return false;
            }
            shortcuts_path = dataset_dir + "/shortcuts.parquet";
            edges_path = dataset_dir + "/edges.csv";
        }

        if (!fs::exists(shortcuts_path) || !fs::exists(edges_path)) {
            std::cerr << "Required files not found: " << std::endl;
            std::cerr << "  Shortcuts: " << shortcuts_path << std::endl;
            std::cerr << "  Edges: " << edges_path << std::endl;
            return false;
        }

        Dataset dataset;
        dataset.name = dataset_name;
        
        std::cout << "Loading shortcuts for " << dataset_name << " from " << shortcuts_path << std::endl;
        dataset.graph.load_shortcuts(shortcuts_path);
        
        std::cout << "Loading edge metadata for " << dataset_name << " from " << edges_path << std::endl;
        dataset.graph.load_edge_metadata(edges_path);

        std::cout << "Loading geometries and building spatial index..." << std::endl;
        std::ifstream file(edges_path);
        std::string line;
        
        // Read header to find column indices
        if (std::getline(file, line)) {
            auto headers = parse_csv_line(line);
            int id_idx = -1;
            int geom_idx = -1;
            
            for (size_t i = 0; i < headers.size(); ++i) {
                if (headers[i] == "id") id_idx = i;
                else if (headers[i] == "geometry") geom_idx = i;
            }

            if (id_idx == -1 || geom_idx == -1) {
                 std::cerr << "Missing id or geometry column in edges.csv" << std::endl;
                 return false;
            }

            while (std::getline(file, line)) {
                if (line.empty()) continue;
                auto columns = parse_csv_line(line);
                if (static_cast<int>(columns.size()) <= std::max(id_idx, geom_idx)) continue;

                try {
                    uint32_t edge_id = std::stoul(columns[id_idx]);
                    std::string wkt = columns[geom_idx];
                    auto points = parse_wkt_linestring(wkt);
                    
                    if (!points.empty()) {
                        dataset.edge_geometries[edge_id] = points;
                        
                        // Add to R-tree
                        double min_lat = points[0].first, max_lat = points[0].first;
                        double min_lon = points[0].second, max_lon = points[0].second;
                        
                        for (const auto& p : points) {
                            min_lat = std::min(min_lat, p.first);
                            max_lat = std::max(max_lat, p.first);
                            min_lon = std::min(min_lon, p.second);
                            max_lon = std::max(max_lon, p.second);
                        }
                        
                        // R-tree stores x=lon, y=lat
                        Box box(Point(min_lon, min_lat), Point(max_lon, max_lat));
                        dataset.rtree.insert(std::make_pair(box, edge_id));
                    }
                } catch (...) {
                    continue;
                }
            }
        }
        
        dataset.loaded = true;
        datasets_[dataset_name] = std::move(dataset);
        
        std::cout << "Successfully loaded dataset: " << dataset_name << std::endl;
        return true;

    } catch (const std::exception& e) {
        std::cerr << "Error loading dataset " << dataset_name << ": " << e.what() << std::endl;
        return false;
    }
}

bool RoutingEngine::unload_dataset(const std::string& dataset_name) {
    auto it = datasets_.find(dataset_name);
    if (it != datasets_.end()) {
        datasets_.erase(it);
        std::cout << "Successfully unloaded dataset: " << dataset_name << std::endl;
        return true;
    }
    return false;
}

std::vector<std::string> RoutingEngine::get_loaded_datasets() const {
    std::vector<std::string> names;
    for (const auto& pair : datasets_) {
        names.push_back(pair.first);
    }
    return names;
}

// Helper to separate implementation
std::vector<std::pair<uint32_t, double>> RoutingEngine::find_nearest_edges_internal(
    const Dataset& dataset,
    double lat, double lng,
    double radius_meters,
    int max_candidates
) {
    std::vector<std::pair<uint32_t, double>> results;
    
    // Convert meters to degrees approx
    double radius_deg = radius_meters / 111320.0;
    
    Box box(Point(lng - radius_deg, lat - radius_deg), 
            Point(lng + radius_deg, lat + radius_deg));
            
    std::vector<Value> rtree_results;
    dataset.rtree.query(bgi::intersects(box) && bgi::nearest(Point(lng, lat), max_candidates), 
                        std::back_inserter(rtree_results));
                        
    for (const auto& res : rtree_results) {
        // Calculate simpler distance for now (from point to box center/edge approx)
        // In reality, we should project point to line string
        double dist = 0.0; // Placeholder for exact distance
        results.push_back({res.second, dist});
    }
    return results;
}


std::vector<std::pair<uint32_t, double>> RoutingEngine::find_nearest_edges(
    const std::string& dataset_name,
    double lat, double lng,
    double radius,
    int max_candidates
) {
    auto it = datasets_.find(dataset_name);
    if (it == datasets_.end()) return {};
    
    return find_nearest_edges_internal(it->second, lat, lng, radius, max_candidates);
}

// Find single nearest edge
std::pair<uint32_t, double> RoutingEngine::find_nearest_edge(
    const std::string& dataset_name,
    double lat, double lng
) {
    auto results = find_nearest_edges(dataset_name, lat, lng, 2000.0, 1);
    if (results.empty()) return {0, std::numeric_limits<double>::max()};
    return results[0];
}


nlohmann::json RoutingEngine::compute_route(
    const std::string& dataset_name,
    double start_lat, double start_lng,
    double end_lat, double end_lng,
    double search_radius,
    int max_candidates
) {
    try {
        auto it = datasets_.find(dataset_name);
        if (it == datasets_.end()) {
            return {{"error", "Dataset not loaded"}, {"success", false}};
        }
        const auto& dataset = it->second;

        // Timers
        using clock = std::chrono::high_resolution_clock;
        
        // 1. Find Nearest Edges
        auto t1 = clock::now();
        auto start_results = find_nearest_edges_internal(dataset, start_lat, start_lng, search_radius, max_candidates);
        auto end_results = find_nearest_edges_internal(dataset, end_lat, end_lng, search_radius, max_candidates);
        auto t2 = clock::now();
        auto time_nearest_us = std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count();

        if (start_results.empty() || end_results.empty()) {
            return {{"error", "No road found near start or end point"}, {"success", false}};
        }

        // Prepare for query_multi_optimized
        std::vector<uint32_t> source_edges;
        std::vector<double> source_dists;
        std::vector<uint32_t> target_edges;
        std::vector<double> target_dists;

        for (const auto& res : start_results) {
            source_edges.push_back(res.first);
            source_dists.push_back(res.second);
        }
        for (const auto& res : end_results) {
            target_edges.push_back(res.first);
            target_dists.push_back(res.second);
        }

        // 2. Run Query
        auto t3 = clock::now();
        auto result = dataset.graph.query_multi_optimized(source_edges, target_edges, source_dists, target_dists);
        auto t4 = clock::now();
        auto time_search_us = std::chrono::duration_cast<std::chrono::microseconds>(t4 - t3).count();

        if (!result.reachable) {
            return {{"error", "No path found"}, {"success", false}};
        }

        // 3. Expand Path
        auto t5 = clock::now();
        auto expanded = dataset.graph.expand_shortcut_path(result.path);
        auto t6 = clock::now();
        auto time_expand_us = std::chrono::duration_cast<std::chrono::microseconds>(t6 - t5).count();

        if (!expanded.success) {
            return {{"error", "Failed to expand path"}, {"success", false}};
        }

        // Helper for distance
        auto haversine_distance = [](double lat1, double lon1, double lat2, double lon2) {
            constexpr double R = 6371000.0;
            double dLat = (lat2 - lat1) * M_PI / 180.0;
            double dLon = (lon2 - lon1) * M_PI / 180.0;
            lat1 = lat1 * M_PI / 180.0;
            lat2 = lat2 * M_PI / 180.0;
            double a = std::sin(dLat / 2) * std::sin(dLat / 2) +
                       std::sin(dLon / 2) * std::sin(dLon / 2) * std::cos(lat1) * std::cos(lat2);
            double c = 2 * std::atan2(std::sqrt(a), std::sqrt(1 - a));
            return R * c;
        };

        // 4. Build GeoJSON and Calculate Distance
        auto t7 = clock::now();
        nlohmann::json coordinates = nlohmann::json::array();
        double total_distance_meters = 0.0;
        
        for (const auto& edge_id : expanded.base_edges) {
            auto geom_it = dataset.edge_geometries.find(edge_id);
            if (geom_it != dataset.edge_geometries.end()) {
                const auto& points = geom_it->second;
                if (points.empty()) continue;

                for (size_t i = 0; i < points.size(); ++i) {
                    // p is {lat, lon}, GeoJSON needs [lon, lat]
                    coordinates.push_back({points[i].second, points[i].first});
                    
                    if (i > 0) {
                        total_distance_meters += haversine_distance(
                            points[i-1].first, points[i-1].second,
                            points[i].first, points[i].second
                        );
                    }
                }
            }
        }

        nlohmann::json geojson = {
            {"type", "Feature"},
            {"geometry", {
                {"type", "LineString"},
                {"coordinates", coordinates}
            }},
            {"properties", {
                {"distance", result.distance}, // optimized cost (time)
                {"length_meters", total_distance_meters} // physical distance
            }}
        };
        auto t8 = clock::now();
        auto time_geojson_us = std::chrono::duration_cast<std::chrono::microseconds>(t8 - t7).count();

        return {
            {"success", true},
            {"dataset", dataset_name},
            {"route", {
                {"distance", result.distance},         // Time/Cost
                {"distance_meters", total_distance_meters}, // Physical Distance
                {"path", expanded.base_edges},
                {"geojson", geojson}
            }},
            {"timing_breakdown", {
                {"find_nearest_us", time_nearest_us},
                {"search_us", time_search_us},
                {"expand_us", time_expand_us},
                {"geojson_us", time_geojson_us}
            }}
        };
    } catch (const std::exception& e) {
        return {
            {"success", false},
            {"error", std::string("Route computation failed: ") + e.what()}
        };
    }
}
