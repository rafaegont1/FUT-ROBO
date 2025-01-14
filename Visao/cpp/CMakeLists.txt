cmake_minimum_required(VERSION 3.5)

# Define the project name
project(vis_comp)

# Generate compilation commands for IDE indexers
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Set the C++ standard to C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Add compile options for GCC/Clang
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find the OpenCV package
find_package(OpenCV REQUIRED)

# Define source files using globbing (this will match all .cpp files in the src directory)
file(GLOB SOURCES "src/*.cpp")

# Create the executable and link it to OpenCV libraries
add_executable(${PROJECT_NAME} ${SOURCES})

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    include
    ${OpenCV_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})
