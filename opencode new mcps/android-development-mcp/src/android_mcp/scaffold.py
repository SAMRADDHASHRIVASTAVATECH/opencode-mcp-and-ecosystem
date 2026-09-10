"""Create Android projects (Compose, Views, library, multi-module)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from android_mcp.config import DEFAULTS, SETTINGS
from android_mcp.env import detect
from android_mcp.errors import ValidationError

TEMPLATES = ("compose-app", "views-app", "library", "multi-module")
ARCHITECTURES = ("none", "mvvm", "clean")


def package_to_path(package: str) -> str:
    return package.replace(".", "/")


def sanitize_package(package: str) -> str:
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$", package):
        raise ValidationError(
            "application_id must be a Java package with at least two segments, e.g. com.example.app"
        )
    return package


def sanitize_name(name: str) -> str:
    if not re.match(r"^[A-Za-z][A-Za-z0-9 _-]{0,40}$", name or ""):
        raise ValidationError("Invalid application name")
    return name.strip()


def versions_for_host() -> dict[str, Any]:
    v = dict(DEFAULTS)
    env = detect()
    rec = env.get("recommended_compile_sdk")
    if rec and rec >= 34:
        v["compile_sdk"] = rec
        v["target_sdk"] = rec
    return v


def create_project(
    dest: Path,
    *,
    name: str,
    application_id: str,
    template: str = "compose-app",
    architecture: str = "mvvm",
    min_sdk: int | None = None,
    compile_sdk: int | None = None,
    target_sdk: int | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    template = template.lower()
    if template not in TEMPLATES:
        raise ValidationError(f"template must be one of {TEMPLATES}")
    if architecture not in ARCHITECTURES:
        raise ValidationError(f"architecture must be one of {ARCHITECTURES}")
    application_id = sanitize_package(application_id)
    name = sanitize_name(name)
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()) and not overwrite:
        raise ValidationError("Destination is not empty; pass overwrite=true")
    ver = versions_for_host()
    if min_sdk:
        ver["min_sdk"] = int(min_sdk)
    if compile_sdk:
        ver["compile_sdk"] = int(compile_sdk)
    if target_sdk:
        ver["target_sdk"] = int(target_sdk)
    ctx = {
        "name": name,
        "application_id": application_id,
        "namespace": application_id,
        "package_path": package_to_path(application_id),
        **{k: str(v) for k, v in ver.items()},
        "architecture": architecture,
    }
    files: list[str] = []
    _write_root(dest, ctx, template, files)
    if template == "multi-module":
        _write_app_module(dest / "app", ctx, "compose-app", architecture, files)
        _write_android_library(dest / "core", {**ctx, "namespace": application_id + ".core"}, files, "core")
        _write_android_library(dest / "feature", {**ctx, "namespace": application_id + ".feature"}, files, "feature")
    elif template == "library":
        _write_android_library(dest / "lib", ctx, files, "lib")
    else:
        _write_app_module(dest / "app", ctx, template, architecture, files)
    env = detect()
    if env.get("sdk_root"):
        (dest / "local.properties").write_text(f"sdk.dir={env['sdk_root']}\n", encoding="utf-8")
        files.append("local.properties")
    return {
        "path": str(dest),
        "template": template,
        "architecture": architecture,
        "application_id": application_id,
        "compile_sdk": int(ctx["compile_sdk"]),
        "min_sdk": int(ctx["min_sdk"]),
        "target_sdk": int(ctx["target_sdk"]),
        "files_written": len(files),
        "files": files[:80],
        "next": [
            "android_inspect_project",
            "Install JDK 17 + Android SDK if android_detect_environment.can_build is false",
            "android_gradle task=assembleDebug",
        ],
        "environment_can_build": env.get("can_build"),
        "missing": env.get("missing"),
    }


def _w(dest: Path, rel: str, content: str, files: list[str]) -> None:
    path = dest / rel if dest.name and rel.startswith("app/") is False else dest / rel
    # dest is already the file root for module writers
    p = dest / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    files.append(str(p))


def _write_root(root: Path, ctx: dict[str, str], template: str, files: list[str]) -> None:
    includes = 'include(":app")'
    if template == "library":
        includes = 'include(":lib")'
    elif template == "multi-module":
        includes = 'include(":app", ":core", ":feature")'
    _w(
        root,
        "settings.gradle.kts",
        f'''
pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}
rootProject.name = "{ctx["name"].replace(" ", "")}"
{includes}
''',
        files,
    )
    plugins = '''
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
}
'''
    if template in {"library", "multi-module"}:
        plugins = '''
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
}
'''
    _w(root, "build.gradle.kts", plugins, files)
    _w(
        root,
        "gradle.properties",
        """
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
""",
        files,
    )
    _w(
        root,
        "gradle/libs.versions.toml",
        f'''
[versions]
agp = "{ctx["agp"]}"
kotlin = "{ctx["kotlin"]}"
coreKtx = "{ctx["core_ktx"]}"
junit = "{ctx["junit"]}"
androidxJunit = "{ctx["androidx_junit"]}"
espressoCore = "{ctx["espresso"]}"
lifecycleRuntimeKtx = "{ctx["lifecycle"]}"
activityCompose = "{ctx["activity_compose"]}"
composeBom = "{ctx["compose_bom"]}"
appcompat = "{ctx["appcompat"]}"
material = "{ctx["material"]}"
constraintlayout = "{ctx["constraintlayout"]}"
navigation = "{ctx["navigation"]}"
room = "{ctx["room"]}"
retrofit = "{ctx["retrofit"]}"
okhttp = "{ctx["okhttp"]}"
coroutines = "{ctx["coroutines"]}"

[libraries]
androidx-core-ktx = {{ group = "androidx.core", name = "core-ktx", version.ref = "coreKtx" }}
junit = {{ group = "junit", name = "junit", version.ref = "junit" }}
androidx-junit = {{ group = "androidx.test.ext", name = "junit", version.ref = "androidxJunit" }}
androidx-espresso-core = {{ group = "androidx.test.espresso", name = "espresso-core", version.ref = "espressoCore" }}
androidx-lifecycle-runtime-ktx = {{ group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version.ref = "lifecycleRuntimeKtx" }}
androidx-lifecycle-viewmodel-ktx = {{ group = "androidx.lifecycle", name = "lifecycle-viewmodel-ktx", version.ref = "lifecycleRuntimeKtx" }}
androidx-lifecycle-viewmodel-compose = {{ group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycleRuntimeKtx" }}
androidx-activity-compose = {{ group = "androidx.activity", name = "activity-compose", version.ref = "activityCompose" }}
androidx-activity = {{ group = "androidx.activity", name = "activity-ktx", version.ref = "activityCompose" }}
androidx-compose-bom = {{ group = "androidx.compose", name = "compose-bom", version.ref = "composeBom" }}
androidx-ui = {{ group = "androidx.compose.ui", name = "ui" }}
androidx-ui-graphics = {{ group = "androidx.compose.ui", name = "ui-graphics" }}
androidx-ui-tooling = {{ group = "androidx.compose.ui", name = "ui-tooling" }}
androidx-ui-tooling-preview = {{ group = "androidx.compose.ui", name = "ui-tooling-preview" }}
androidx-ui-test-manifest = {{ group = "androidx.compose.ui", name = "ui-test-manifest" }}
androidx-ui-test-junit4 = {{ group = "androidx.compose.ui", name = "ui-test-junit4" }}
androidx-material3 = {{ group = "androidx.compose.material3", name = "material3" }}
androidx-navigation-compose = {{ group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }}
androidx-appcompat = {{ group = "androidx.appcompat", name = "appcompat", version.ref = "appcompat" }}
material = {{ group = "com.google.android.material", name = "material", version.ref = "material" }}
androidx-constraintlayout = {{ group = "androidx.constraintlayout", name = "constraintlayout", version.ref = "constraintlayout" }}
androidx-room-runtime = {{ group = "androidx.room", name = "room-runtime", version.ref = "room" }}
androidx-room-ktx = {{ group = "androidx.room", name = "room-ktx", version.ref = "room" }}
retrofit = {{ group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }}
okhttp = {{ group = "com.squareup.okhttp3", name = "okhttp", version.ref = "okhttp" }}
kotlinx-coroutines-android = {{ group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-android", version.ref = "coroutines" }}

[plugins]
android-application = {{ id = "com.android.application", version.ref = "agp" }}
android-library = {{ id = "com.android.library", version.ref = "agp" }}
kotlin-android = {{ id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }}
kotlin-compose = {{ id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }}
''',
        files,
    )
    _w(
        root,
        "gradle/wrapper/gradle-wrapper.properties",
        f"""
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-{ctx["gradle"]}-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""",
        files,
    )
    _w(
        root,
        "gradlew",
        """#!/usr/bin/env sh
# Minimal Gradle wrapper launcher. Generate the real wrapper with: gradle wrapper
DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
if [ -f "$DIR/gradle/wrapper/gradle-wrapper.jar" ]; then
  exec java -jar "$DIR/gradle/wrapper/gradle-wrapper.jar" "$@"
fi
if command -v gradle >/dev/null 2>&1; then
  exec gradle "$@"
fi
echo "Missing gradle-wrapper.jar and gradle. Install Gradle or Android Studio and run: gradle wrapper" >&2
exit 1
""",
        files,
    )
    try:
        (root / "gradlew").chmod(0o755)
    except OSError:
        pass
    _w(
        root,
        ".gitignore",
        """
.gradle/
build/
local.properties
*.iml
.idea/
.DS_Store
captures/
*.apk
*.aab
*.keystore
!debug.keystore
""",
        files,
    )
    _w(root, "README.md", f"# {ctx['name']}\n\nGenerated by Android Development MCP.\n", files)


def _sdk_block(ctx: dict[str, str], library: bool = False) -> str:
    app_id = "" if library else f'        applicationId = "{ctx["application_id"]}"\n'
    return f'''
    namespace = "{ctx.get("namespace", ctx["application_id"])}"
    compileSdk = {ctx["compile_sdk"]}
    defaultConfig {{
{app_id}        minSdk = {ctx["min_sdk"]}
        targetSdk = {ctx["target_sdk"]}
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }}
    buildTypes {{
        release {{
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }}
    }}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}
    kotlinOptions {{ jvmTarget = "17" }}
'''


def _write_app_module(app: Path, ctx: dict[str, str], template: str, architecture: str, files: list[str]) -> None:
    compose = template == "compose-app"
    plugins = """
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
"""
    if compose:
        plugins += "    alias(libs.plugins.kotlin.compose)\n"
    plugins += "}\n"
    features = '    buildFeatures { compose = true }\n' if compose else "    buildFeatures { viewBinding = true }\n"
    deps = """
dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.ktx)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
"""
    if compose:
        deps += """
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.navigation.compose)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
"""
    else:
        deps += """
    implementation(libs.androidx.appcompat)
    implementation(libs.material)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.activity)
"""
    deps += "}\n"
    _w(app, "build.gradle.kts", plugins + "\nandroid {\n" + _sdk_block(ctx) + features + "}\n" + deps, files)
    _w(app, "proguard-rules.pro", "# Add project-specific ProGuard rules here.\n", files)
    theme_parent = "Theme.Material3.DayNight.NoActionBar" if compose else "Theme.Material3.DayNight"
    _w(
        app,
        "src/main/AndroidManifest.xml",
        f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="true"
        android:icon="@android:drawable/ic_menu_info_details"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.App"
        android:networkSecurityConfig="@xml/network_security_config">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
''',
        files,
    )
    _w(app, "src/main/res/values/strings.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{ctx["name"]}</string>
</resources>
''', files)
    _w(app, "src/main/res/values/themes.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.App" parent="{theme_parent}" />
</resources>
''', files)
    _w(app, "src/main/res/xml/network_security_config.xml", '''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
</network-security-config>
''', files)
    pkg = ctx["package_path"]
    if compose:
        _write_compose_sources(app, ctx, architecture, pkg, files)
    else:
        _write_view_sources(app, ctx, architecture, pkg, files)
    _w(
        app,
        f"src/test/java/{pkg}/ExampleUnitTest.kt",
        f'''
package {ctx["application_id"]}
import org.junit.Assert.assertEquals
import org.junit.Test
class ExampleUnitTest {{
    @Test fun addition_isCorrect() {{ assertEquals(4, 2 + 2) }}
}}
''',
        files,
    )
    _w(
        app,
        f"src/androidTest/java/{pkg}/ExampleInstrumentedTest.kt",
        f'''
package {ctx["application_id"]}
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
@RunWith(AndroidJUnit4::class)
class ExampleInstrumentedTest {{
    @Test fun useAppContext() {{
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals("{ctx["application_id"]}", appContext.packageName)
    }}
}}
''',
        files,
    )


def _write_compose_sources(app: Path, ctx: dict[str, str], architecture: str, pkg: str, files: list[str]) -> None:
    _w(
        app,
        f"src/main/java/{pkg}/ui/theme/Theme.kt",
        f'''
package {ctx["application_id"]}.ui.theme
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
@Composable
fun AppTheme(content: @Composable () -> Unit) {{
    val dark = isSystemInDarkTheme()
    MaterialTheme(colorScheme = if (dark) darkColorScheme() else lightColorScheme(), content = content)
}}
''',
        files,
    )
    extra_imports = ""
    extra_body = "Greeting(name = \"" + ctx["name"] + "\")"
    if architecture in {"mvvm", "clean"}:
        extra_imports = f"import {ctx['application_id']}.ui.HomeScreen\n"
        extra_body = "HomeScreen()"
        _w(
            app,
            f"src/main/java/{pkg}/data/GreetingRepository.kt",
            f'''
package {ctx["application_id"]}.data
class GreetingRepository {{
    fun greeting(): String = "Hello from {ctx["name"]}"
}}
''',
            files,
        )
        _w(
            app,
            f"src/main/java/{pkg}/ui/HomeViewModel.kt",
            f'''
package {ctx["application_id"]}.ui
import androidx.lifecycle.ViewModel
import {ctx["application_id"]}.data.GreetingRepository
class HomeViewModel(
    private val repository: GreetingRepository = GreetingRepository()
) : ViewModel() {{
    val message: String = repository.greeting()
}}
''',
            files,
        )
        _w(
            app,
            f"src/main/java/{pkg}/ui/HomeScreen.kt",
            f'''
package {ctx["application_id"]}.ui
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
@Composable
fun HomeScreen(vm: HomeViewModel = viewModel()) {{
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {{
        Text(vm.message)
    }}
}}
''',
            files,
        )
        if architecture == "clean":
            _w(
                app,
                f"src/main/java/{pkg}/domain/GetGreetingUseCase.kt",
                f'''
package {ctx["application_id"]}.domain
import {ctx["application_id"]}.data.GreetingRepository
class GetGreetingUseCase(private val repository: GreetingRepository = GreetingRepository()) {{
    operator fun invoke(): String = repository.greeting()
}}
''',
                files,
            )
    _w(
        app,
        f"src/main/java/{pkg}/MainActivity.kt",
        f'''
package {ctx["application_id"]}
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import {ctx["application_id"]}.ui.theme.AppTheme
{extra_imports}
class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {{
            AppTheme {{
                {extra_body}
            }}
        }}
    }}
}}
@Composable
fun Greeting(name: String) {{ Text(text = "Hello $name") }}
''',
        files,
    )


def _write_view_sources(app: Path, ctx: dict[str, str], architecture: str, pkg: str, files: list[str]) -> None:
    _w(
        app,
        "src/main/res/layout/activity_main.xml",
        '''<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextView
        android:id="@+id/message"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/app_name"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
</androidx.constraintlayout.widget.ConstraintLayout>
''',
        files,
    )
    _w(
        app,
        f"src/main/java/{pkg}/MainActivity.kt",
        f'''
package {ctx["application_id"]}
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }}
}}
''',
        files,
    )
    if architecture in {"mvvm", "clean"}:
        _w(
            app,
            f"src/main/java/{pkg}/data/GreetingRepository.kt",
            f'''
package {ctx["application_id"]}.data
class GreetingRepository {{ fun greeting(): String = "Hello from {ctx["name"]}" }}
''',
            files,
        )
        _w(
            app,
            f"src/main/java/{pkg}/ui/HomeViewModel.kt",
            f'''
package {ctx["application_id"]}.ui
import androidx.lifecycle.ViewModel
import {ctx["application_id"]}.data.GreetingRepository
class HomeViewModel(private val repository: GreetingRepository = GreetingRepository()) : ViewModel() {{
    val message: String = repository.greeting()
}}
''',
            files,
        )


def _write_android_library(mod: Path, ctx: dict[str, str], files: list[str], name: str) -> None:
    _w(
        mod,
        "build.gradle.kts",
        f'''
plugins {{
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}}
android {{
{_sdk_block(ctx, library=True)}
}}
dependencies {{
    implementation(libs.androidx.core.ktx)
    testImplementation(libs.junit)
}}
''',
        files,
    )
    pkg = ctx["package_path"] if "package_path" in ctx else package_to_path(ctx["namespace"])
    # namespace may differ
    pkg = package_to_path(ctx["namespace"])
    _w(
        mod,
        f"src/main/java/{pkg}/Placeholder.kt",
        f'package {ctx["namespace"]}\nclass Placeholder\n',
        files,
    )
    _w(mod, "src/main/AndroidManifest.xml", '<?xml version="1.0" encoding="utf-8"?>\n<manifest />\n', files)
    _ = SETTINGS
