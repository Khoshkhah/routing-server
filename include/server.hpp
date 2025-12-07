#pragma once

#include "routing_engine.hpp"
#include <crow.h>
#include <nlohmann/json.hpp>
#include <string>
#include <memory>

class RoutingServer {
public:
    RoutingServer();
    ~RoutingServer() = default;

    void load_config(const std::string& config_file);
    void run();

private:
    // HTTP handlers
    crow::response handle_health_check();
    crow::response handle_route(const crow::request& req);
    crow::response handle_load_dataset(const crow::request& req);

    // Configuration
    struct Config {
        int port = 8080;
        std::string host = "0.0.0.0";
        int thread_count = 4;
        std::string datasets_path = "../routing-pipeline/data";
    } config_;

    // Components
    std::unique_ptr<RoutingEngine> routing_engine_;
    crow::SimpleApp app_;
};