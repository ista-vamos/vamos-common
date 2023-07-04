cmake_minimum_required(VERSION 3.9)
project(vamos-common LANGUAGES CXX VERSION 0.1)

set(CMAKE_VERBOSE_MAKEFILE 1)
set(CMAKE_CXX_STANDARD 17)
#set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

#find_package(vamos-buffers REQUIRED)

#if(NOT CMAKE_BUILD_TYPE)
#        message(STATUS "Build type not set. Setting buffer's build type.")
#        set(CMAKE_BUILD_TYPE ${vamos-buffers_BUILD_TYPE} CACHE STRING "" FORCE)
#endif()

#if (vamos-buffers_OPTION_ENABLE_IPO)
#        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
#endif()

#include_directories(${vamos_buffers_INCLUDE_DIRS})

#get_filename_component(vamos-buffers_DIR ${vamos-buffers_DIR} ABSOLUTE)
#get_target_property(vamos-buffers_vamos-buffers-lib vamos-buffers-lib LOCATION)
#get_target_property(vamos-buffers_vamos-buffers-ringbuf vamos-buffers-ringbuf LOCATION)
#get_target_property(vamos-buffers_vamos-buffers-shmbuf vamos-buffers-shmbuf LOCATION)
#get_target_property(vamos-buffers_vamos-buffers-streams vamos-buffers-streams LOCATION)
#get_filename_component(vamos-buffers_LIBRARIES_DIRS_lib ${vamos-buffers_vamos-buffers-lib} DIRECTORY)
#get_filename_component(vamos-buffers_LIBRARIES_DIRS_core ${vamos-buffers_vamos-buffers-ringbuf} DIRECTORY)
#get_filename_component(vamos-buffers_LIBRARIES_DIRS_shmbuf ${vamos-buffers_vamos-buffers-shmbuf} DIRECTORY)
#get_filename_component(vamos-buffers_LIBRARIES_DIRS_streams ${vamos-buffers_vamos-buffers-streams} DIRECTORY)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.py.in
               ${CMAKE_CURRENT_SOURCE_DIR}/config.py)

#enable_testing()
#add_subdirectory(tests)

#install(EXPORT vamos-sources_Export
#        FILE vamos-sources.cmake
#        DESTINATION lib/cmake/vamos-sources.cmake)
#export(EXPORT vamos-sources_Export FILE ${CMAKE_CURRENT_BINARY_DIR}/cmake/vamos-sources/vamos-sources.cmake)

include(CMakePackageConfigHelpers)

configure_package_config_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake/vamos-common/vamos-common-config.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/cmake/vamos-common/vamos-common-config.cmake"
  INSTALL_DESTINATION "lib/cmake/vamos-common"
  NO_SET_AND_CHECK_MACRO
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
  )

write_basic_package_version_file(
    "vamos-common-version.cmake"
    VERSION ${vamos-common_VERSION}
    COMPATIBILITY AnyNewerVersion)

install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/cmake/vamos-common/vamos-common-config.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/cmake/vamos-common/vamos-common-version.cmake"
  DESTINATION lib/cmake/vamos-common)
