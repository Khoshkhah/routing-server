#include "server.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <chrono> // Added for std::chrono

RoutingServer::RoutingServer() : routing_engine_(std::make_unique<RoutingEngine>()) {
    // Setup routes
    // Route: Find nearest edge
    CROW_ROUTE(app_, "/nearest_edge")
    .methods("GET"_method, "POST"_method)
    ([this](const crow::request& req) {
        auto start_time = std::chrono::high_resolution_clock::now();
        nlohmann::json response;
        
        try {
            // Parse arguments (support both GET and POST)
            std::string dataset_name;
            double lat = 0.0, lon = 0.0;
            
            if (req.method == "GET"_method) {
                if (req.url_params.get("dataset")) dataset_name = req.url_params.get("dataset");
                if (req.url_params.get("lat")) lat = std::stod(req.url_params.get("lat"));
                if (req.url_params.get("lon")) lon = std::stod(req.url_params.get("lon"));
            } else {
                auto body = nlohmann::json::parse(req.body);
                if (body.contains("dataset")) dataset_name = body["dataset"];
                if (body.contains("lat")) lat = body["lat"];
                if (body.contains("lon")) lon = body["lon"];
            }

            if (dataset_name.empty()) {
                response["success"] = false;
                response["error"] = "Missing dataset parameter";
                return crow::response(400, response.dump());
            }

            // Perform search
            auto nearest = routing_engine_->find_nearest_edge(dataset_name, lat, lon);
            
            if (nearest.first == 0 && nearest.second > 1000000) { // Assuming invalid result check
                 // In our implementation, 0 *could* be valid, but max_double distance implies failure
                 // Let's assume find_nearest_edge throws or returns reasonable defaults
            }

            response["success"] = true;
            response["edge_id"] = nearest.first;
            response["distance_meters"] = nearest.second;
            
            auto end_time = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
            response["runtime_ms"] = duration.count() / 1000.0;

            return crow::response(200, response.dump());

        } catch (const std::exception& e) {
            response["success"] = false;
            response["error"] = e.what();
            return crow::response(500, response.dump());
        }
    });

    // Route: Find multiple nearest edges
    CROW_ROUTE(app_, "/nearest_edges")
    .methods("GET"_method, "POST"_method)
    ([this](const crow::request& req) {
        nlohmann::json response;
        try {
            std::string dataset_name;
            double lat = 0.0, lon = 0.0;
            double radius = 1000.0;
            int max_candidates = 5;

            if (req.method == "GET"_method) {
                if (req.url_params.get("dataset")) dataset_name = req.url_params.get("dataset");
                if (req.url_params.get("lat")) lat = std::stod(req.url_params.get("lat"));
                if (req.url_params.get("lon")) lon = std::stod(req.url_params.get("lon"));
                if (req.url_params.get("radius")) radius = std::stod(req.url_params.get("radius"));
                if (req.url_params.get("max_candidates")) max_candidates = std::stoi(req.url_params.get("max_candidates"));
            } else {
                auto body = nlohmann::json::parse(req.body);
                if (body.contains("dataset")) dataset_name = body["dataset"];
                if (body.contains("lat")) lat = body["lat"];
                if (body.contains("lon")) lon = body["lon"];
                if (body.contains("radius")) radius = body["radius"];
                if (body.contains("max_candidates")) max_candidates = body["max_candidates"];
            }

            if (dataset_name.empty()) {
                response["success"] = false;
                response["error"] = "Missing parameters";
                return crow::response(400, response.dump());
            }

            auto edges = routing_engine_->find_nearest_edges(dataset_name, lat, lon, radius, max_candidates);
            
            nlohmann::json edges_json = nlohmann::json::array();
            for(const auto& p : edges) {
                edges_json.push_back({{"id", p.first}, {"distance", p.second}});
            }
            
            response["success"] = true;
            response["edges"] = edges_json;
            return crow::response(200, response.dump());
            
        } catch (const std::exception& e) {
             response["success"] = false;
             response["error"] = e.what();
             return crow::response(500, response.dump());
        }
    });
    // Route: Compute shortest path
    CROW_ROUTE(app_, "/health")([this]() { return handle_health_check(); });
    CROW_ROUTE(app_, "/route").methods("POST"_method)([this](const crow::request& req) { return handle_route(req); });
    CROW_ROUTE(app_, "/load_dataset").methods("POST"_method)([this](const crow::request& req) { return handle_load_dataset(req); });
}

void RoutingServer::load_config(const std::string& config_file) {
    try {
        std::ifstream file(config_file);
        if (file.is_open()) {
            nlohmann::json j;
            file >> j;

            if (j.contains("port")) config_.port = j["port"];
            if (j.contains("host")) config_.host = j["host"];
            if (j.contains("thread_count")) config_.thread_count = j["thread_count"];
            if (j.contains("datasets_path")) config_.datasets_path = j["datasets_path"];
        }
    } catch (const std::exception& e) {
        std::cerr << "Warning: Could not load config file " << config_file << ": " << e.what() << std::endl;
        std::cerr << "Using default configuration." << std::endl;
    }
}

void RoutingServer::run() {
    std::cout << "Server starting on " << config_.host << ":" << config_.port << std::endl;
    app_.port(config_.port).bindaddr(config_.host).multithreaded().run();
}

crow::response RoutingServer::handle_health_check() {
    nlohmann::json response = {
        {"status", "healthy"},
        {"datasets_loaded", routing_engine_->get_loaded_datasets()}
    };
    return crow::response(200, response.dump());
}

crow::response RoutingServer::handle_route(const crow::request& req) {
    try {
        auto json_body = nlohmann::json::parse(req.body);

        std::string dataset = json_body["dataset"];
        double start_lat = json_body["start_lat"];
        double start_lng = json_body["start_lng"];
        double end_lat = json_body["end_lat"];
        double end_lng = json_body["end_lng"];
        double search_radius = json_body.value("search_radius", 1000.0);
        int max_candidates = json_body.value("max_candidates", 10);

        auto route = routing_engine_->compute_route(
            dataset, start_lat, start_lng, end_lat, end_lng,
            search_radius, max_candidates
        );

        nlohmann::json response = {
            {"success", true},
            {"route", route}
        };

        return crow::response(200, response.dump());

    } catch (const std::exception& e) {
        nlohmann::json error_response = {
            {"success", false},
            {"error", e.what()}
        };
        return crow::response(400, error_response.dump());
    }
}

crow::response RoutingServer::handle_load_dataset(const crow::request& req) {
    try {
        auto json_body = nlohmann::json::parse(req.body);
        std::string dataset = json_body["dataset"];

        bool success = routing_engine_->load_dataset(dataset, config_.datasets_path);

        nlohmann::json response = {
            {"success", success},
            {"dataset", dataset}
        };

        return crow::response(success ? 200 : 400, response.dump());

    } catch (const std::exception& e) {
        nlohmann::json error_response = {
            {"success", false},
            {"error", e.what()}
        };
        return crow::response(400, error_response.dump());
    }
}