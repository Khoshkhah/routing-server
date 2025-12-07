#pragma once

#include <nlohmann/json.hpp>
#include <string>
#include <unordered_map>
#include <vector>
#include <memory>
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/geometry/geometries/box.hpp>
#include <boost/geometry/index/rtree.hpp>

#include "shortcut_graph.hpp"

namespace bg = boost::geometry;
namespace bgi = boost::geometry::index;

using Point = bg::model::point<double, 2, bg::cs::cartesian>; // Lon, Lat
using Box = bg::model::box<Point>;
using Value = std::pair<Box, uint32_t>; // Bounding box, Edge ID

class RoutingEngine {
public:
    RoutingEngine();
    ~RoutingEngine() = default;

    struct Dataset {
        std::string name;
        bool loaded = false;
        ShortcutGraph graph;
        bgi::rtree< Value, bgi::quadratic<16> > rtree;
        // Map from edge ID to geometry (WKT or sequence of points)
        std::unordered_map<uint32_t, std::vector<std::pair<double, double>>> edge_geometries; 
    };

    bool load_dataset(const std::string& dataset_name, const std::string& datasets_path);
    nlohmann::json compute_route(
        const std::string& dataset,
        double start_lat, double start_lng,
        double end_lat, double end_lng,
        double search_radius = 1000.0,
        int max_candidates = 10
    );
    std::vector<std::string> get_loaded_datasets() const;

private:
    std::unordered_map<std::string, Dataset> datasets_;

    // Helper methods
    std::vector<std::pair<uint32_t, double>> find_nearest_edges(
        const std::string& dataset_name,
        double lat, double lng,
        double radius = 1000.0,
        int max_candidates = 5
    );
    
    std::pair<uint32_t, double> find_nearest_edge(
        const std::string& dataset_name,
        double lat, double lng
    );

    // Internal helper
    std::vector<std::pair<uint32_t, double>> find_nearest_edges_internal(
        const Dataset& dataset,
        double lat, double lng,
        double radius,
        int max_candidates
    );

    nlohmann::json run_contraction_hierarchies(
        const Dataset& dataset,
        const std::vector<std::pair<double, double>>& start_candidates,
        const std::vector<std::pair<double, double>>& end_candidates
    );
};