#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
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
    description =   "Magnum-Plugins — Lightweight and modular C++11/C++14 \
                    graphics middleware for games and data visualization"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "corrade", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/ulricheck/conan-magnum-plugins"
    homepage = "https://magnum.graphics"
    author = "ulrich eck (forked on github)"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "patches/macos_jsonhpp_fix.diff"]
    generators = "cmake"
    short_paths = True  # Some folders go out of the 260 chars path length scope (windows)

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
        "with_tinygltfimporter": False,
    }

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "magnum/2020.06@camposs/stable"
    )

    def system_package_architecture(self):
        if tools.os_info.with_apt:
            if self.settings.arch == "x86":
                return ':i386'
            elif self.settings.arch == "x86_64":
                return ':amd64'
            elif self.settings.arch == "armv6" or self.settings.arch == "armv7":
                return ':armel'
            elif self.settings.arch == "armv7hf":
                return ':armhf'
            elif self.settings.arch == "armv8":
                return ':arm64'

        if tools.os_info.with_yum:
            if self.settings.arch == "x86":
                return '.i686'
            elif self.settings.arch == 'x86_64':
                return '.x86_64'
        return ""

    # def system_requirements(self):
    #     # Install required OpenGL stuff on linux
    #     if tools.os_info.is_linux:
    #         if tools.os_info.with_apt:
    #             installer = tools.SystemPackageTool()

    #             packages = []
    #             if self.options.target_gl:
    #                 packages.append("libgl1-mesa-dev")
    #             if self.options.target_gles:
    #                 packages.append("libgles1-mesa-dev")

    #             arch_suffix = self.system_package_architecture()
    #             for package in packages:
    #                 installer.install("%s%s" % (package, arch_suffix))

    #         elif tools.os_info.with_yum:
    #             installer = tools.SystemPackageTool()

    #             arch_suffix = self.system_package_architecture()
    #             packages = []
    #             if self.options.target_gl:
    #                 packages.append("mesa-libGL-devel")
    #             if self.options.target_gles:
    #                 packages.append("mesa-libGLES-devel")

    #             for package in packages:
    #                 installer.install("%s%s" % (package, arch_suffix))
    #         else:
    #             self.output.warn("Could not determine package manager, skipping Linux system requirements installation.")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):

        # To fix issue with resource management, see here:
        # https://github.com/mosra/magnum/issues/304#issuecomment-451768389
        bps = self.options['magnum'].build_plugins_static
        self.options.build_plugins_static = bps if bps is not None else True
        shared = self.options['magnum'].shared
        self.options.shared = shared if shared is not None else False

        if self.options.with_assimpimporter:
            self.options['magnum'].add_option('with_anyimageimporter', True)

    def requirements(self):
        if self.options.with_assimpimporter:
            self.requires("assimp/4.1.0@camposs/stable")

    def source(self):
        source_url = "https://github.com/mosra/magnum-plugins"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "MagnumPlugins", "AssimpImporter", "CMakeLists.txt"),
            "target_link_libraries(AssimpImporter PUBLIC Magnum::Trade Assimp::Assimp",
            "target_link_libraries(AssimpImporter PUBLIC Magnum::Trade CONAN_PKG::assimp")

    def _configure_cmake(self):
        cmake = CMake(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str 
            cmake.definitions[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        # Magnum uses suffix on the resulting 'lib'-folder when running cmake.install()
        # Set it explicitly to empty, else Magnum might set it implicitly (eg. to "64")
        add_cmake_option("LIB_SUFFIX", "")

        add_cmake_option("BUILD_STATIC", not self.options.shared)
        add_cmake_option("BUILD_STATIC_PIC", not self.options.shared and self.options.get_safe("fPIC"))

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        tools.patch(self._source_subfolder, "patches/macos_jsonhpp_fix.diff")
        cmake = self._configure_cmake()
        cmake.verbose = True
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                if not self.options.shared:
                    self.cpp_info.libs.append("OpenGL32.lib")
            else:
                self.cpp_info.libs.append("opengl32")
        else:
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.libs.append("GL")
