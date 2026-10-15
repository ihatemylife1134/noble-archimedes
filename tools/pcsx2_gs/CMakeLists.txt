cmake_minimum_required(VERSION 3.24)
project(NoblePcsx2GsConsumer LANGUAGES C CXX ASM_MASM)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY MultiThreadedDLL)
if(NOT MSVC)
 message(FATAL_ERROR "Supported Windows MSVC/clang-cl ABI required")
endif()
if(NOT PCSX2_SOURCE OR NOT PCSX2_DEPS)
 message(FATAL_ERROR "Pinned source and official dependency paths required")
endif()
# Consumer-owned source inventory generated from the pinned upstream lists.
include("${CMAKE_CURRENT_BINARY_DIR}/sources.cmake")
set(CPUINFO_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
set(CPUINFO_BUILD_UNIT_TESTS OFF CACHE BOOL "" FORCE)
set(CPUINFO_BUILD_MOCK_TESTS OFF CACHE BOOL "" FORCE)
set(CPUINFO_BUILD_BENCHMARKS OFF CACHE BOOL "" FORCE)
set(CPUINFO_LIBRARY_TYPE static CACHE STRING "" FORCE)
set(CPUINFO_RUNTIME_TYPE shared CACHE STRING "" FORCE)
add_subdirectory("${PCSX2_SOURCE}/3rdparty/cpuinfo" cpuinfo EXCLUDE_FROM_ALL)
add_subdirectory("${PCSX2_SOURCE}/3rdparty/lzma" lzma EXCLUDE_FROM_ALL)
add_library(noble_pcsx2_gs SHARED consumer.cpp host_glue.cpp ${NOBLE_GS_SOURCES})
target_compile_options(noble_pcsx2_gs PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:/O2;/Gy;/Gw;/EHsc;/fp:precise;/Zc:__cplusplus;/Zc:preprocessor;/Zc:externConstexpr;/permissive-;/bigobj;/utf-8>")
target_compile_definitions(noble_pcsx2_gs PRIVATE _M_X86=1 __SSE4_1__=1 _M_SSE=0x401 UNICODE _UNICODE NOMINMAX WIN32_LEAN_AND_MEAN _CRT_SECURE_NO_WARNINGS FMT_HEADER_ONLY)
target_include_directories(noble_pcsx2_gs PRIVATE
 "${PCSX2_SOURCE}" "${PCSX2_SOURCE}/pcsx2" "${PCSX2_SOURCE}/common" "${PCSX2_SOURCE}/3rdparty/include"
 "${PCSX2_DEPS}/include" "${PCSX2_DEPS}/include/freetype2" "${PCSX2_SOURCE}/3rdparty/fmt/include" "${PCSX2_SOURCE}/3rdparty/fast_float/include"
 "${PCSX2_SOURCE}/3rdparty/imgui/include" "${PCSX2_SOURCE}/3rdparty/imgui/src"
 "${PCSX2_SOURCE}/3rdparty/winwil/include" "${PCSX2_SOURCE}/3rdparty/D3D12MemAlloc/include"
 "${PCSX2_SOURCE}/3rdparty/winpixeventruntime/include" "${PCSX2_SOURCE}/3rdparty/zydis/include"
 "${PCSX2_SOURCE}/3rdparty/zydis/dependencies/zycore/include" "${PCSX2_SOURCE}/3rdparty/libzip/lib"
 "${PCSX2_SOURCE}/3rdparty/xbyak"
 "${PCSX2_SOURCE}/3rdparty/lzma/include" "${PCSX2_SOURCE}/3rdparty/cpuinfo/include"
 "${CMAKE_CURRENT_BINARY_DIR}/generated")
file(GLOB NOBLE_DEP_LIBS "${PCSX2_DEPS}/lib/*.lib")
target_link_libraries(noble_pcsx2_gs PRIVATE ${NOBLE_DEP_LIBS} cpuinfo LZMA::LZMA
 d3d11 d3d12 dxgi d3dcompiler dxguid winmm pathcch shlwapi shell32 ole32 oleaut32 user32 gdi32 dbghelp version dwmapi winhttp ws2_32 psapi OneCore)
target_link_options(noble_pcsx2_gs PRIVATE /OPT:REF /OPT:ICF)
set_target_properties(noble_pcsx2_gs PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/../bin")
