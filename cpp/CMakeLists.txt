cmake_minimum_required(VERSION 3.15)
project(DroneTrajectory)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find ONNX Runtime
# You may need to set ONNXRUNTIME_DIR to point to your installation
# Example: cmake -DONNXRUNTIME_DIR=/path/to/onnxruntime ..

# Windows-specific: Add common installation paths
if(WIN32)
    list(APPEND ONNX_SEARCH_PATHS
        "${CMAKE_SOURCE_DIR}/../onnxruntime-win-x64-1.17.1"
        "${CMAKE_SOURCE_DIR}/../onnxruntime-win-x64-1.16.3"
        "${CMAKE_SOURCE_DIR}/../onnxruntime-win-x64-1.16.0"
        "$ENV{ProgramFiles}/onnxruntime"
        "$ENV{ProgramFiles(x86)}/onnxruntime"
        "C:/Program Files/onnxruntime"
        "C:/onnxruntime"
        "${CMAKE_SOURCE_DIR}/../onnxruntime"
        "${CMAKE_SOURCE_DIR}/../../onnxruntime"
    )
endif()

find_path(ONNXRUNTIME_INCLUDE_DIR
    NAMES onnxruntime_cxx_api.h
    HINTS
        ${ONNXRUNTIME_DIR}/include
        ${ONNX_SEARCH_PATHS}
        /usr/include/onnxruntime
        /usr/local/include/onnxruntime
        $ENV{HOME}/.local/include/onnxruntime
    PATH_SUFFIXES
        include
        include/onnxruntime
        include/onnxruntime/core/session
)

find_library(ONNXRUNTIME_LIBRARY
    NAMES onnxruntime onnxruntime.lib
    HINTS
        ${ONNXRUNTIME_DIR}/lib
        ${ONNX_SEARCH_PATHS}
        /usr/lib
        /usr/local/lib
        $ENV{HOME}/.local/lib
    PATH_SUFFIXES
        lib
        lib/Release
        lib/Debug
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

# Windows-specific: Copy ONNX Runtime DLL to output directory
if(WIN32 AND ONNXRUNTIME_LIBRARY)
    get_filename_component(ONNXRUNTIME_LIB_DIR ${ONNXRUNTIME_LIBRARY} DIRECTORY)
    find_file(ONNXRUNTIME_DLL
        NAMES onnxruntime.dll
        HINTS ${ONNXRUNTIME_LIB_DIR}
        PATH_SUFFIXES ../bin bin
    )
    if(ONNXRUNTIME_DLL)
        message(STATUS "Found ONNX Runtime DLL: ${ONNXRUNTIME_DLL}")
        # Copy DLL to build directory after build
        add_custom_command(TARGET drone_trajectory_lib POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                ${ONNXRUNTIME_DLL}
                $<TARGET_FILE_DIR:drone_trajectory_lib>
            COMMENT "Copying ONNX Runtime DLL to output directory"
        )
    endif()
endif()

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

# Windows-specific: Copy ONNX Runtime DLL for executable
if(WIN32 AND ONNXRUNTIME_DLL)
    add_custom_command(TARGET drone_trajectory_cpp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${ONNXRUNTIME_DLL}
            $<TARGET_FILE_DIR:drone_trajectory_cpp>
        COMMENT "Copying ONNX Runtime DLL to executable directory"
    )
endif()

# Print build info
message(STATUS "")
message(STATUS "Build Configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Platform: ${CMAKE_SYSTEM_NAME}")
if(WIN32)
    message(STATUS "  Generator: ${CMAKE_GENERATOR}")
endif()
message(STATUS "")
