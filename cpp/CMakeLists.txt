cmake_minimum_required(VERSION 3.15)
project(DroneTrajectory)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find ONNX Runtime
# You may need to set ONNXRUNTIME_DIR to point to your installation
# Example: cmake -DONNXRUNTIME_DIR=/path/to/onnxruntime ..

find_path(ONNXRUNTIME_INCLUDE_DIR
    NAMES onnxruntime_cxx_api.h
    HINTS
        ${ONNXRUNTIME_DIR}/include
        /usr/include/onnxruntime
        /usr/local/include/onnxruntime
        $ENV{HOME}/.local/include/onnxruntime
)

find_library(ONNXRUNTIME_LIBRARY
    NAMES onnxruntime
    HINTS
        ${ONNXRUNTIME_DIR}/lib
        /usr/lib
        /usr/local/lib
        $ENV{HOME}/.local/lib
)

if(NOT ONNXRUNTIME_INCLUDE_DIR OR NOT ONNXRUNTIME_LIBRARY)
    message(STATUS "ONNX Runtime not found automatically. You may need to set ONNXRUNTIME_DIR")
    message(STATUS "Attempting to use system paths...")
    
    # Try alternative locations
    set(ONNXRUNTIME_INCLUDE_DIR "/usr/include/onnxruntime/core/session" CACHE PATH "ONNX Runtime include directory")
    set(ONNXRUNTIME_LIBRARY "onnxruntime" CACHE FILEPATH "ONNX Runtime library")
endif()

message(STATUS "ONNX Runtime include: ${ONNXRUNTIME_INCLUDE_DIR}")
message(STATUS "ONNX Runtime library: ${ONNXRUNTIME_LIBRARY}")

# Create library
add_library(drone_trajectory_lib STATIC
    drone_trajectory.cpp
    drone_trajectory.h
)

target_include_directories(drone_trajectory_lib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${ONNXRUNTIME_INCLUDE_DIR}
)

target_link_libraries(drone_trajectory_lib PUBLIC
    ${ONNXRUNTIME_LIBRARY}
)

# Create executable
add_executable(drone_trajectory_cpp
    main.cpp
)

target_link_libraries(drone_trajectory_cpp PRIVATE
    drone_trajectory_lib
)

# Installation
install(TARGETS drone_trajectory_cpp drone_trajectory_lib
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(FILES drone_trajectory.h
    DESTINATION include
)

# Print build info
message(STATUS "")
message(STATUS "Build Configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "")
