#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.build import can_run
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        corrade_root = self.dependencies["corrade"].package_folder
        tc.variables["Corrade_ROOT"] = corrade_root
        magnum_root = self.dependencies["magnum"].package_folder
        tc.variables["Magnum_ROOT"] = magnum_root
        magnum_plugins_root = self.dependencies["magnum-plugins"].package_folder
        tc.variables["MagnumPlugins_ROOT"] = magnum_plugins_root
        assimp_root = self.dependencies["assimp"].package_folder
        tc.variables["Assimp_ROOT"] = assimp_root
        self.output.info("Assimp_ROOT: {}".format(assimp_root))
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("magnum", "cmake_find_mode", "none")
        deps.set_property("magnum-plugins", "cmake_find_mode", "none")
        deps.set_property("assimp", "cmake_find_mode", "module")
        deps.set_property("assimp", "cmake_file_name", "Assimp")
        deps.set_property("assimp", "cmake_target_name", "Assimp::Assimp")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(cmd, env="conanrun")
