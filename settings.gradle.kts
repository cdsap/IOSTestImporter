plugins {
    id("com.gradle.develocity") version "4.3"
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

develocity {
    server = "https://ge.solutions-team.gradle.com/"
    allowUntrustedServer = true
    edgeDiscovery = true
    buildScan {
        publishing.onlyIf { it.isAuthenticated }
        obfuscation {
            ipAddresses { addresses -> addresses.map { "0.0.0.0" } }
        }
    }
}
rootProject.name = "test1"
