#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, collect_libs, get, replace_in_file, patch
from conan.tools.microsoft.visual import check_min_vs
from conan.tools.system.package_manager import Apt
import os



def sort_libs(correct_order, libs, lib_suffix='', reverse_result=False):
    # Add suffix for correct string matching
    correct_order[:] = [s.__add__(lib_suffix) for s in correct_order]

    result = []
    for expectedLib in correct_order:
        for lib in libs:
            if expectedLib == lib:
                result.append(lib)

    if reverse_result:
        # Linking happens in reversed order
        result.reverse()

    return result

class LibnameConan(ConanFile):
    name = "magnum-plugins"
    version = "2020.06"
    description = "Magnum-Plugins — Lightweight and modular C++11/C++14 \
                    graphics middleware for games and data visualization"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "corrade", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/TUM-CONAN/conan-magnum-plugins"
    homepage = "https://magnum.graphics"
    author = "ulrich eck (forked on github)"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "patches/macos_jsonhpp_fix.diff"]

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "build_plugins_static": [True, False], 
        "fPIC": [True, False],
        "with_assimpimporter": [True, False],
        "with_ddsimporter": [True, False],
        "with_devilimageimporter": [True, False],
        "with_drflacaudioimporter": [True, False],
        "with_drwavaudioimporter": [True, False],
        "with_faad2audioimporter": [True, False],
        "with_freetypefont": [True, False],
        "with_harfbuzzfont": [True, False],
        "with_jpegimageconverter": [True, False],
        "with_jpegimporter": [True, False],
        "with_miniexrimageconverter": [True, False],
        "with_openddl": [True, False],
        "with_opengeximporter": [True, False],
        "with_pngimageconverter": [True, False],
        "with_pngimporter": [True, False],
        "with_stanfordimporter": [True, False],
        "with_stbimageconverter": [True, False],
        "with_stbimageimporter": [True, False],
        "with_stbtruetypefont": [True, False],
        "with_stbvorbisaudioimporter": [True, False],
        "with_stlimporter": [True, False],
        "with_tinygltfimporter": [True, False],
    }
    default_options = {
        "shared": False,
        "build_plugins_static": False,
        "fPIC": True,
        "with_assimpimporter": True,
        "with_ddsimporter": False,
        "with_devilimageimporter": False,
        "with_drflacaudioimporter": False,
        "with_drwavaudioimporter": False,
        "with_faad2audioimporter": False,
        "with_freetypefont": False,
        "with_harfbuzzfont": False,
        "with_jpegimageconverter": False,
        "with_jpegimporter": False,
        "with_miniexrimageconverter": False,
        "with_openddl": False,
        "with_opengeximporter": False,
        "with_pngimageconverter": False,
        "with_pngimporter": False,
        "with_stanfordimporter": False,
        "with_stbimageconverter": False,
        "with_stbimageimporter": False,
        "with_stbtruetypefont": False,
        "with_stbvorbisaudioimporter": False,
        "with_stlimporter": False,
        "with_tinygltfimporter": False,
    }

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):

        # To fix issue with resource management, see here:
        # https://github.com/mosra/magnum/issues/304#issuecomment-451768389

        if self.options.with_assimpimporter:
            self.options['magnum']['with_anyimageimporter'] = True

    def requirements(self):
        self.requires("magnum/2020.06@camposs/stable")
        if self.options.with_assimpimporter:
            self.requires("assimp/5.2.2")

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "v{}".format(self.version),
            "url": "https://github.com/mosra/magnum-plugins.git"
            }}
            )

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "find_package(Magnum REQUIRED)",
            "cmake_policy(SET CMP0074 NEW)\nfind_package(Magnum REQUIRED)")

        # patch(self, self.source_folder, os.path.join("patches", "macos_jsonhpp_fix.diff"))

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        # Corrade uses suffix on the resulting 'lib'-folder when running cmake.install()
        # Set it explicitly to empty, else Corrade might set it implicitly (eg. to "64")
        add_cmake_option("LIB_SUFFIX", "")

        add_cmake_option("BUILD_STATIC", not self.options.shared)
        add_cmake_option("BUILD_STATIC_PIC", not self.options.shared and self.options.get_safe("fPIC"))
        corrade_root = self.dependencies["corrade"].package_folder
        tc.variables["Corrade_ROOT"] = corrade_root
        magnum_root = self.dependencies["magnum"].package_folder
        tc.variables["Magnum_ROOT"] = magnum_root
        assimp_root = self.dependencies["assimp"].package_folder
        tc.variables["Assimp_ROOT"] = assimp_root

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("magnum", "cmake_find_mode", "none")
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("assimp", "cmake_find_mode", "module")
        deps.set_property("assimp", "cmake_file_name", "Assimp")
        deps.set_property("assimp", "cmake_target_name", "Assimp::Assimp")
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_subfolder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Windows":
            if self.settings.compiler == "msvc":
                if not self.options.shared:
                    self.cpp_info.libs.append("OpenGL32.lib")
            else:
                self.cpp_info.libs.append("opengl32")
        else:
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.libs.append("GL")
