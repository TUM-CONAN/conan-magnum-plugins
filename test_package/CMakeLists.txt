cmake_minimum_required(VERSION 3.15)
cmake_policy(SET CMP0074 NEW)

project(test_package)
set(CMAKE_VERBOSE_MAKEFILE TRUE)

set(CMAKE_MODULE_PATH "${MagnumPlugins_ROOT}/share/cmake/MagnumPlugins" ${CMAKE_MODULE_PATH})
message(STATUS "Added CMAKE_MODULE_PATH: ${MagnumPlugins_ROOT}")
set(CMAKE_MODULE_PATH "${Magnum_ROOT}/share/cmake/Magnum" ${CMAKE_MODULE_PATH})
message(STATUS "Added CMAKE_MODULE_PATH: ${Magnum_ROOT}")
find_package(Magnum REQUIRED GL Shaders Primitives MeshTools Trade)
find_package(MagnumPlugins REQUIRED AssimpImporter)
set_directory_properties(PROPERTIES CORRADE_USE_PEDANTIC_FLAGS ON)


add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Magnum::GL Magnum::Shaders Magnum::Trade
    Magnum::Primitives Magnum::MeshTools MagnumPlugins::AssimpImporter)

set_target_properties(${PROJECT_NAME} 
    PROPERTIES 
    	CXX_STANDARD 11
    	CXX_STANDARD_REQUIRED ON
    	CXX_EXTENSIONS OFF
)