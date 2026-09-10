// OLCAP Phone Call Management - Android module build script.
// NOTE: needs JDK 17+ and Android SDK. Open this project in Android Studio and
// let it sync + download the Gradle wrapper, or install the SDK and run
// `./gradlew :app:assembleDebug`. It cannot be compiled in a plain Linux sandbox
// without the Android SDK.
plugins {
    id("com.android.application") version "8.5.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
