#!/usr/bin/env python3
"""Produce iOS-only diagnostic source copies; fail if an upstream seam changes."""
import argparse
from pathlib import Path


def replace_once(source, marker, replacement):
    if source.count(marker) != 1:
        raise ValueError(f'iOS diagnostic seam changed: {marker!r}')
    return source.replace(marker, replacement)


def metal_source(source, header):
    source = f'#include "{header}"\n' + source
    marker = '    m_drawable = MRCRetain([m_layer nextDrawable]);'
    source = replace_once(source, marker,
        '    const double ssx_acquire_start = CACurrentMediaTime();\n' + marker +
        '\n    SSXDrawableAcquired(ssx_acquire_start, m_drawable != nullptr);')
    marker = '    if (m_drawable)\n    {'
    return replace_once(source, marker, marker +
        '\n      SSXDrawableSubmitted(m_drawable, g_state_tracker->GetRenderCmdBuf());')


def state_source(source, header):
    source = f'#include "{header}"\n#include <cerrno>\n' + source
    for marker, replacement in [
        ('  const std::string& filename = save_args.filename;',
         '  const std::string& filename = save_args.filename;\n'
         '  SSXCheckpointStage("writer_started", filename.c_str(), buffer.size(), 0);'),
        ('    Core::DisplayMessage("Failed to create state file", 2000);',
         '    SSXCheckpointStage("create_failed", filename.c_str(), 0, errno);\n'
         '    Core::DisplayMessage("Failed to create state file", 2000);'),
        ('  if (!f.IsGood())\n    Core::DisplayMessage("Failed to write state file", 2000);',
         '  if (!f.IsGood())\n  {\n'
         '    SSXCheckpointStage("write_failed", filename.c_str(), buffer.size(), errno);\n'
         '    Core::DisplayMessage("Failed to write state file", 2000);\n  }'),
        ('  if (!f.Close())\n    Core::DisplayMessage("Failed to close state file", 2000);',
         '  if (!f.Close())\n  {\n'
         '    SSXCheckpointStage("close_failed", filename.c_str(), buffer.size(), errno);\n'
         '    Core::DisplayMessage("Failed to close state file", 2000);\n  }'),
        ('    Core::DisplayMessage("Failed to rename state file", 2000);',
         '    SSXCheckpointStage("rename_failed", filename.c_str(), buffer.size(), errno);\n'
         '    Core::DisplayMessage("Failed to rename state file", 2000);'),
        ('    const std::filesystem::path temp_path(filename);',
         '    SSXCheckpointStage("file_ready", filename.c_str(), buffer.size(), 0);\n'
         '    const std::filesystem::path temp_path(filename);'),
        ('static void SaveAsFromCore(Core::System& system, std::string filename)\n{',
         'static void SaveAsFromCore(Core::System& system, std::string filename)\n{\n'
         '  SSXCheckpointStage("serialize_started", filename.c_str(), 0, 0);'),
        ('    buffer.assign(buffer.extract().first, actual_size);',
         '    SSXCheckpointStage("serialize_complete", filename.c_str(), actual_size, 0);\n'
         '    buffer.assign(buffer.extract().first, actual_size);'),
        ('    Core::DisplayMessage("Unable to save: Internal DoState Error", 4000);',
         '    SSXCheckpointStage("serialize_failed", filename.c_str(), 0, 0);\n'
         '    Core::DisplayMessage("Unable to save: Internal DoState Error", 4000);'),
        ('void SaveAs(Core::System& system, std::string filename)\n{',
         'void SaveAs(Core::System& system, std::string filename)\n{\n'
         '  SSXCheckpointStage("cpu_requested", filename.c_str(), 0, 0);'),
    ]:
        source = replace_once(source, marker, replacement)
    return source


def run_source(source, header):
    marker = 'void StaticRecompCore::Run()\n{'
    source = replace_once(source, marker, f'#include "{header}"\n' + marker +
                          '\n  u64 ssx_next_sample = 0, ssx_last_sample_tick = 0;')
    marker = '    core_timing.Advance();'
    return replace_once(source, marker, marker + '''
    const u64 ssx_ticks = core_timing.GetTicks();
    if (ssx_ticks >= ssx_next_sample || ssx_ticks < ssx_last_sample_tick) {
      SSXRecompSample(ssx_ticks, m_native_dispatches, m_fallback_steps, m_fallback_jit_runs,
                      m_native_exceptions, m_hle_returns, m_hle_vectors, m_hle_rejects);
      ssx_next_sample = ssx_ticks + m_system.GetSystemTimers().GetTicksPerSecond();
    }
    ssx_last_sample_tick = ssx_ticks;''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--header', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run', type=Path, help='Instrument the already-generated native trial source copy')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for relative, name, transform in [
        ('Core/State.cpp', 'DiagnosticState.cpp', state_source),
        ('VideoBackends/Metal/MTLGfx.mm', 'DiagnosticMTLGfx.mm', metal_source),
    ]:
        text = transform((args.core / 'Source/Core' / relative).read_text(), args.header.resolve())
        destination = args.output / name
        if not destination.exists() or destination.read_text() != text:
            destination.write_text(text)
    if args.run:
        args.run.write_text(run_source(args.run.read_text(), args.header.resolve()))


if __name__ == '__main__':
    main()
