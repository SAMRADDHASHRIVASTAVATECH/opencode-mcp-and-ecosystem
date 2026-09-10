# Supported formats
Built-in identification: ELF, PE including .NET indicator, Mach-O/fat, JVM class, JAR, APK, DEX, WASM, ZIP containers and possible PYC. Current local execution supports generic strings/file triage and GNU-binutils native metadata/disassembly; Python source is parsed/compiled/disassembled without execution.

Catalog-routed support when tools are installed: native formats/firmware via Ghidra/radare2, .NET via ILSpyCmd, Android via JADX, JVM via CFR/Javap, WASM via WABT, and Python bytecode via version-compatible external decompilers. “Supported” never means exact original-source recovery.
