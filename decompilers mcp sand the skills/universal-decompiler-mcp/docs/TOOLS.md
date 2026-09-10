# Tool ecosystem
Locally discovered: file/libmagic CLI and GNU `readelf`, `objdump`, `nm`, `strings`, `c++filt`, `ar`; Java runtime and unzip/tar. Not detected in the build sandbox: Ghidra, radare2, JADX, CFR, JDK `javap`, ILSpy/.NET, WABT, Python decompilers, LIEF, pefile, Capstone, YARA, binwalk or 7-Zip.

Catalog adapters cover Ghidra headless for native decompilation, radare2 for scriptable binary analysis, JADX for APK/DEX, CFR for JVM classes/JARs, ILSpyCmd for managed assemblies, WABT for WASM, version-matched Python bytecode tools, LIEF and pefile. Availability is always re-probed.
