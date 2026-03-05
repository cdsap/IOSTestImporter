import com.gradle.develocity.agent.gradle.test.ImportJUnitXmlReports
import com.gradle.develocity.agent.gradle.test.JUnitXmlDialect
plugins {
    base
}

tasks.register("import") {
    doLast {
        println("Import task executed")
    }
}

afterEvaluate {
    ImportJUnitXmlReports.register(
        tasks,
        tasks.named("import"),
        JUnitXmlDialect.GENERIC,
    )
        .configure {
            reports.from(file("test-report.xml")) 
    
        }
}