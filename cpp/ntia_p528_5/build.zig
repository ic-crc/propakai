const std = @import("std");

const cpp_sources = &.{
    "src/p528/CombineDistributions.cpp",
    "src/p528/data.cpp",
    "src/p528/FindKForYpiAt99Percent.cpp",
    "src/p528/GetPathLoss.cpp",
    "src/p528/InverseComplementaryCumulativeDistributionFunction.cpp",
    "src/p528/LinearInterpolation.cpp",
    "src/p528/LineOfSight.cpp",
    "src/p528/LongTermVariability.cpp",
    "src/p528/NakagamiRice.cpp",
    "src/p528/P528.cpp",
    "src/p528/RayOptics.cpp",
    "src/p528/ReflectionCoefficients.cpp",
    "src/p528/SmoothEarthDiffraction.cpp",
    "src/p528/TerminalGeometry.cpp",
    "src/p528/TranshorizonSearch.cpp",
    "src/p528/Troposcatter.cpp",
    "src/p528/ValidateInputs.cpp",
    "src/p676/GlobalWetPressure.cpp",
    "src/p676/LineShapeFactor.cpp",
    "src/p676/NonresonantDebyeAttenuation.cpp",
    "src/p676/OxygenData.cpp",
    "src/p676/RayTrace.cpp",
    "src/p676/RefractiveIndex.cpp",
    "src/p676/Refractivity.cpp",
    "src/p676/SlantPath.cpp",
    "src/p676/SpecificAttenuation.cpp",
    "src/p676/TerrestrialPath.cpp",
    "src/p676/WaterVapourData.cpp",
    "src/p676/WaterVapourDensityToPartialPressure.cpp",
    "src/p835/Conversions.cpp",
    "src/p835/MeanAnnualGlobalReferenceAtmosphere.cpp",
};

const cpp_flags = &.{
    "-std=c++17",
    "-Wall",
    "-fPIC",
};

const bin_path = "../../../propakai/bin";

const CrossTarget = struct {
    query: std.Target.Query,
    output_name: []const u8,
    output_dir: []const u8,
};

const cross_targets = &[_]CrossTarget{
    .{
        .query = .{
            .os_tag = .windows,
            .cpu_arch = .x86_64,
            .abi = .gnu,
        },
        .output_name = "p528_5",
        .output_dir = "win/x86_64",
    },
    .{
        .query = .{
            .os_tag = .windows,
            .cpu_arch = .aarch64,
            .abi = .gnu,
        },
        .output_name = "p528_5",
        .output_dir = "win/arm64",
    },
    .{
        .query = .{
            .os_tag = .linux,
            .cpu_arch = .x86_64,
            .abi = .gnu,
            .glibc_version = .{ .major = 2, .minor = 17, .patch = 0 },
        },
        .output_name = "p528_5",
        .output_dir = "linux/x86_64",
    },
    .{
        .query = .{
            .os_tag = .linux,
            .cpu_arch = .aarch64,
            .abi = .gnu,
            .glibc_version = .{ .major = 2, .minor = 17, .patch = 0 },
        },
        .output_name = "p528_5",
        .output_dir = "linux/arm64",
    },
    .{
        .query = .{
            .os_tag = .macos,
            .cpu_arch = .x86_64,
            .abi = .none,
            .os_version_min = .{ .semver = .{ .major = 11, .minor = 0, .patch = 0 } },
        },
        .output_name = "p528_5",
        .output_dir = "macos/x86_64",
    },
    .{
        .query = .{
            .os_tag = .macos,
            .cpu_arch = .aarch64,
            .abi = .none,
            .os_version_min = .{ .semver = .{ .major = 11, .minor = 0, .patch = 0 } },
        },
        .output_name = "p528_5",
        .output_dir = "macos/arm64",
    },
};

pub fn build(b: *std.Build) void {
    for (cross_targets) |ct| {
        const resolved_target = b.resolveTargetQuery(ct.query);

        const module = b.createModule(.{
            .target = resolved_target,
            .optimize = .ReleaseSafe,
            .link_libcpp = true,
            .link_libc = true,
            .strip = true, // removes debug info
        });

        module.addCSourceFiles(.{ .files = cpp_sources, .flags = cpp_flags });
        //module.addIncludePath(b.path("src"));
        module.addIncludePath(b.path("include"));

        const lib = b.addLibrary(.{
            .name = ct.output_name,
            .root_module = module,
            .linkage = .dynamic,
        });

        // zig-out install
        const install = b.addInstallArtifact(lib, .{
            .dest_dir = .{
                .override = .{
                    .custom = ct.output_dir,
                },
            },
            .dest_sub_path = switch (ct.query.os_tag.?) {
                .windows => b.fmt("{s}.dll", .{ct.output_name}),
                .macos => b.fmt("{s}.dylib", .{ct.output_name}),
                .linux => b.fmt("{s}.so", .{ct.output_name}),
                else => ct.output_name,
            },
        });
        b.getInstallStep().dependOn(&install.step);

        // install to propakai/bin directory
        const bin_install = b.addInstallArtifact(lib, .{
            .dest_dir = .{
                .override = .{
                    .custom = b.pathJoin(&.{ bin_path, ct.output_dir }),
                },
            },
            .dest_sub_path = switch (ct.query.os_tag.?) {
                .windows => b.fmt("{s}.dll", .{ct.output_name}),
                .macos => b.fmt("{s}.dylib", .{ct.output_name}),
                .linux => b.fmt("{s}.so", .{ct.output_name}),
                else => ct.output_name,
            },
        });
        b.getInstallStep().dependOn(&bin_install.step);
    }
}
