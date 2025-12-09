#include <gtest/gtest.h>
#include "routing_engine.hpp"

// Basic test for routing engine
TEST(RoutingEngineTest, DatasetLoading) {
    RoutingEngine engine;

    // Test loading a non-existent dataset
    EXPECT_FALSE(engine.load_dataset("nonexistent", "/tmp"));

    // Test getting loaded datasets on empty engine
    auto datasets = engine.get_loaded_datasets();
    EXPECT_TRUE(datasets.empty());
}

// Basic test for route computation
TEST(RoutingEngineTest, RouteComputation) {
    RoutingEngine engine;

    // Test route computation without loaded dataset
    auto result = engine.compute_route("test", 0, 0, 1, 1, 1000, 5);
    EXPECT_FALSE(result["success"]);

    // Check error message
    EXPECT_TRUE(result.contains("error"));
}

TEST(RoutingEngineTest, RouteComputationOneToOne) {
    RoutingEngine engine;
    auto result = engine.compute_route("test", 0, 0, 1, 1, 1000, 5, "one_to_one");
    EXPECT_FALSE(result["success"]);
    EXPECT_TRUE(result.contains("error"));
}

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}