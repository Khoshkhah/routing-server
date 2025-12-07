#include "server.hpp"
#include <iostream>

int main(int argc, char* argv[]) {
    try {
        // Initialize server
        RoutingServer server;

        // Load configuration
        std::string config_file = "config/server_config.json";
        if (argc > 1) {
            config_file = argv[1];
        }

        server.load_config(config_file);

        // Start server
        std::cout << "Starting routing server..." << std::endl;
        server.run();

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}