from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, replace_in_file, update_conandata
from conan.tools.microsoft import check_min_vs
from conan.tools.scm import Git
import os


required_conan_version = ">=2.28"


_PLUGIN_OPTIONS = (
    "with_assimpimporter",
    "with_astcimporter",
    "with_avifimporter",
    "with_basisimageconverter",
    "with_basisimporter",
    "with_bcdecimageconverter",
    "with_cgltfimporter",
    "with_ddsimporter",
    "with_devilimageimporter",
    "with_drflacaudioimporter",
    "with_drmp3audioimporter",
    "with_drwavaudioimporter",
    "with_etcdecimageconverter",
    "with_faad2audioimporter",
    "with_freetypefont",
    "with_glslangshaderconverter",
    "with_gltfimporter",
    "with_gltfsceneconverter",
    "with_harfbuzzfont",
    "with_icoimporter",
    "with_jpegimageconverter",
    "with_jpegimporter",
    "with_ktximageconverter",
    "with_ktximporter",
    "with_lunasvgimporter",
    "with_meshoptimizersceneconverter",
    "with_miniexrimageconverter",
    "with_openddl",
    "with_openexrimageconverter",
    "with_openexrimporter",
    "with_opengeximporter",
    "with_plutosvgimporter",
    "with_pngimageconverter",
    "with_pngimporter",
    "with_primitiveimporter",
    "with_resvgimporter",
    "with_spirvtoolsshaderconverter",
    "with_spngimporter",
    "with_stanfordimporter",
    "with_stanfordsceneconverter",
    "with_stbdxtimageconverter",
    "with_stbimageconverter",
    "with_stbimageimporter",
    "with_stbresizeimageconverter",
    "with_stbtruetypefont",
    "with_stbvorbisaudioimporter",
    "with_stlimporter",
    "with_tinygltfimporter",
    "with_ufbximporter",
    "with_webpimageconverter",
    "with_webpimporter",
)


class MagnumPluginsConan(ConanFile):
    name = "magnum-plugins"
    version = "2026.dev"
    description = "Lightweight and modular plugins for the Magnum graphics middleware"
    topics = ("corrade", "magnum", "graphics", "rendering", "3d", "2d", "plugins")
    url = "https://github.com/TUM-CONAN/conan-magnum-plugins"
    homepage = "https://magnum.graphics"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    exports = "LICENSE.md"
    exports_sources = "patches/*"

    options = {
        "shared": [True, False],
        "build_plugins_static": [True, False],
        "fPIC": [True, False],
        **{option: [True, False] for option in _PLUGIN_OPTIONS},
    }
    default_options = {
        "shared": False,
        "build_plugins_static": False,
        "fPIC": True,
        **{option: False for option in _PLUGIN_OPTIONS},
        "libbasisu/*:with_zstd": False,
    }

    _source_commit = "47703ec6dff0d6d4e469cbc1277cfcf15b0be260"

    def export(self):
        update_conandata(self, {"sources": {
            "commit": self._source_commit,
            "url": "https://github.com/mosra/magnum-plugins.git",
        }})

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["corrade"].shared = True
            self.options["magnum"].shared = True

        self.options["magnum"].build_plugins_static = self.options.build_plugins_static

        if self._needs_magnum_anyimageimporter:
            self.options["magnum"].with_anyimageimporter = True
        if self._needs_magnum_audio:
            self.options["magnum"].with_audio = True
            self.options["magnum"].with_anyaudioimporter = True
        if self._needs_magnum_text:
            self.options["magnum"].with_text = True
        if self._needs_magnum_trade:
            self.options["magnum"].with_trade = True
        if self._needs_magnum_meshtools:
            self.options["magnum"].with_meshtools = True
        if self.options.with_primitiveimporter:
            self.options["magnum"].with_primitives = True
        if self._needs_magnum_shadertools:
            self.options["magnum"].with_shadertools = True

    def requirements(self):
        self.requires("magnum/2026.dev@camposs/stable", transitive_headers=True, transitive_libs=True)

        if self.options.with_assimpimporter:
            self.requires("assimp/6.0.2", transitive_libs=True)
        if self.options.with_avifimporter:
            self.requires("libavif/1.4.1", transitive_libs=True)
        if self.options.with_basisimageconverter or self.options.with_basisimporter:
            self.requires("libbasisu/1.15.0", transitive_libs=True)
        if self.options.with_devilimageimporter:
            self.requires("devil/1.8.0", transitive_libs=True)
        if self.options.with_freetypefont or self.options.with_harfbuzzfont:
            self.requires("freetype/2.14.3", transitive_libs=True)
        if self.options.with_glslangshaderconverter:
            self.requires("glslang/1.4.350.0", transitive_libs=True)
        if self.options.with_harfbuzzfont:
            self.requires("harfbuzz/12.3.0", transitive_libs=True)
        if self.options.with_jpegimageconverter or self.options.with_jpegimporter:
            self.requires("libjpeg/9f", transitive_libs=True)
        if self.options.with_lunasvgimporter:
            self.requires("lunasvg/3.5.0", transitive_libs=True)
        if self.options.with_meshoptimizersceneconverter:
            self.requires("meshoptimizer/1.0", transitive_libs=True)
        if self.options.with_openexrimageconverter or self.options.with_openexrimporter:
            self.requires("openexr/3.4.12", transitive_libs=True)
        if self.options.with_plutosvgimporter:
            self.requires("plutosvg/0.0.7", transitive_libs=True)
        if self.options.with_pngimageconverter or self.options.with_pngimporter:
            self.requires("libpng/1.6.58", transitive_libs=True)
        if self.options.with_spirvtoolsshaderconverter:
            self.requires("spirv-tools/1.4.350.0", transitive_libs=True)
        if self.options.with_spngimporter:
            self.requires("libspng/0.7.4", transitive_libs=True)
        if self.options.with_webpimageconverter or self.options.with_webpimporter:
            self.requires("libwebp/1.6.0", transitive_libs=True)

    def validate(self):
        if self.settings.os == "Windows":
            check_min_vs(self, "191")

        unsupported = {
            "with_faad2audioimporter": "FAAD2 is not available in the configured Conan Center/Camposs remotes",
            "with_resvgimporter": "resvg is not available in the configured Conan Center/Camposs remotes",
        }
        for option, reason in unsupported.items():
            if self.options.get_safe(option):
                raise ConanInvalidConfiguration(f"{option}=True is unsupported: {reason}")

        if self.options.with_cgltfimporter or self.options.with_tinygltfimporter:
            raise ConanInvalidConfiguration(
                "CgltfImporter and TinyGltfImporter are upstream deprecated plugins and require "
                "Magnum built with build_deprecated=True; use with_gltfimporter instead."
            )

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIB_SUFFIX"] = ""
        tc.variables["MAGNUM_BUILD_STATIC"] = not self.options.shared
        tc.variables["MAGNUM_BUILD_STATIC_PIC"] = not self.options.shared and self.options.get_safe("fPIC", False)
        tc.variables["MAGNUM_BUILD_PLUGINS_STATIC"] = self.options.build_plugins_static
        tc.variables["MAGNUM_BUILD_TESTS"] = False
        tc.variables["MAGNUM_BUILD_GL_TESTS"] = False

        for option in _PLUGIN_OPTIONS:
            cmake_name = option.removeprefix("with_").upper()
            tc.variables[f"MAGNUM_WITH_{cmake_name}"] = self.options.get_safe(option)

        for dep_name, cmake_name in (
            ("corrade", "Corrade"),
            ("magnum", "Magnum"),
            ("assimp", "Assimp"),
            ("libbasisu", "BasisUniversal"),
        ):
            if dep_name in self.dependencies:
                tc.variables[f"{cmake_name}_ROOT"] = self.dependencies[dep_name].package_folder.replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("corrade", "cmake_find_mode", "none")
        deps.set_property("magnum", "cmake_find_mode", "none")
        deps.set_property("assimp", "cmake_find_mode", "module")
        deps.set_property("assimp", "cmake_file_name", "Assimp")
        deps.set_property("assimp", "cmake_target_name", "Assimp::Assimp")
        deps.set_property("devil", "cmake_find_mode", "module")
        deps.set_property("devil", "cmake_file_name", "DevIL")
        deps.set_property("freetype", "cmake_file_name", "Freetype")
        deps.set_property("harfbuzz", "cmake_file_name", "HarfBuzz")
        deps.set_property("libjpeg", "cmake_file_name", "JPEG")
        deps.set_property("libpng", "cmake_file_name", "PNG")
        deps.set_property("libspng", "cmake_find_mode", "module")
        deps.set_property("libspng", "cmake_file_name", "Spng")
        deps.set_property("libspng", "cmake_target_name", "Spng::Spng")
        deps.set_property("libwebp", "cmake_find_mode", "module")
        deps.set_property("libwebp", "cmake_file_name", "WebP")
        deps.set_property("libwebp", "cmake_target_name", "WebP::WebP")
        deps.set_property("spirv-tools", "cmake_find_mode", "module")
        deps.set_property("spirv-tools", "cmake_file_name", "SpirvTools")
        deps.set_property("zstd", "cmake_find_mode", "module")
        deps.set_property("zstd", "cmake_file_name", "Zstd")
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_subfolder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.builddirs = [os.path.join("share", "cmake", "MagnumPlugins")]
        self.cpp_info.set_property("cmake_file_name", "MagnumPlugins")
        self.cpp_info.set_property("cmake_find_mode", "none")

        if self.settings.os == "Windows":
            if self.settings.compiler == "msvc":
                if not self.options.shared:
                    self.cpp_info.system_libs.append("OpenGL32.lib")
            else:
                self.cpp_info.system_libs.append("opengl32")
        else:
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.system_libs.append("GL")

    @property
    def _needs_magnum_anyimageimporter(self):
        return any(
            self.options.get_safe(option)
            for option in (
                "with_assimpimporter",
                "with_cgltfimporter",
                "with_gltfimporter",
                "with_opengeximporter",
                "with_tinygltfimporter",
                "with_ufbximporter",
            )
        )

    @property
    def _needs_magnum_audio(self):
        return any(self.options.get_safe(option) for option in _PLUGIN_OPTIONS if option.endswith("audioimporter"))

    @property
    def _needs_magnum_text(self):
        return any(
            self.options.get_safe(option)
            for option in (
                "with_freetypefont",
                "with_harfbuzzfont",
                "with_stbtruetypefont",
            )
        )

    @property
    def _needs_magnum_trade(self):
        return any(
            self.options.get_safe(option)
            for option in _PLUGIN_OPTIONS
            if option.endswith(("importer", "imageconverter", "sceneconverter"))
        )

    @property
    def _needs_magnum_meshtools(self):
        return any(
            self.options.get_safe(option)
            for option in (
                "with_meshoptimizersceneconverter",
                "with_stanfordimporter",
                "with_stanfordsceneconverter",
                "with_ufbximporter",
            )
        )

    @property
    def _needs_magnum_shadertools(self):
        return self.options.with_glslangshaderconverter or self.options.with_spirvtoolsshaderconverter

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "project(MagnumPlugins CXX)",
            'project(MagnumPlugins CXX)\nset(CMAKE_POLICY_VERSION_MINIMUM "3.5" CACHE STRING "" FORCE)',
        )
        find_basis = os.path.join(self.source_folder, "modules", "FindBasisUniversal.cmake")
        replace_in_file(
            self,
            find_basis,
            "find_library(BasisUniversalEncoder_LIBRARY_RELEASE basisu_encoder)",
            "find_library(BasisUniversalEncoder_LIBRARY_RELEASE NAMES basisu_encoder basisu)",
        )
        replace_in_file(
            self,
            find_basis,
            "find_library(BasisUniversalEncoder_LIBRARY_DEBUG basisu_encoder HINTS \"debug\")",
            "find_library(BasisUniversalEncoder_LIBRARY_DEBUG NAMES basisu_encoder basisu HINTS \"debug\")",
        )
        replace_in_file(
            self,
            find_basis,
            'find_path(BasisUniversalEncoder_INCLUDE_DIR basisu_enc.h PATH_SUFFIXES "basisu/encoder")',
            'find_path(BasisUniversalEncoder_INCLUDE_DIR basisu_enc.h PATH_SUFFIXES "basisu/encoder" "libbasisu/encoder")',
        )
        replace_in_file(
            self,
            find_basis,
            "find_library(BasisUniversalTranscoder_LIBRARY_RELEASE basisu_transcoder)",
            "find_library(BasisUniversalTranscoder_LIBRARY_RELEASE NAMES basisu_transcoder basisu)",
        )
        replace_in_file(
            self,
            find_basis,
            "find_library(BasisUniversalTranscoder_LIBRARY_DEBUG basisu_transcoder HINTS \"debug\")",
            "find_library(BasisUniversalTranscoder_LIBRARY_DEBUG NAMES basisu_transcoder basisu HINTS \"debug\")",
        )
        replace_in_file(
            self,
            find_basis,
            'find_path(BasisUniversalTranscoder_INCLUDE_DIR transcoder/basisu_transcoder.h PATH_SUFFIXES "basisu")',
            'find_path(BasisUniversalTranscoder_INCLUDE_DIR transcoder/basisu_transcoder.h PATH_SUFFIXES "basisu" "libbasisu")',
        )
