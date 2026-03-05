//
//  test1Tests.swift
//  test1Tests
//
//  Created by inaki villar on 2/22/26.
//

import XCTest
@testable import test1

final class test1Tests: XCTestCase {
    private var logic: GreetingLogic!

    override func setUpWithError() throws {
        logic = GreetingLogic()
    }

    override func tearDownWithError() throws {
        logic = nil
    }

    func testGreetingWithNilNameReturnsDefaultGreeting() {
        let result = logic.greeting(name: nil)

        XCTAssertEqual(result, "Hello, world!")
    }

    func testGreetingWithEmptyNameReturnsDefaultGreeting() {
        let result = logic.greeting(name: "")

        XCTAssertEqual(result, "Hello, world!")
    }

    func testGreetingWithWhitespaceNameReturnsDefaultGreeting() {
        let result = logic.greeting(name: "   \n  ")

        XCTAssertEqual(result, "Hello, world!")
    }

    func testGreetingWithNameReturnsPersonalizedGreeting() {
        let result = logic.greeting(name: "Inaki")

        XCTAssertEqual(result, "Hello, WRONG!", "Expected personalized greeting for Inaki")
    }

    func testGreetingTrimsLeadingAndTrailingWhitespace() {
        let result = logic.greeting(name: "  Inaki  ")

        XCTAssertEqual(result, "Hello, Inaki!")
    }

    func testSymbolNameWhenOnlineIsGlobe() {
        let result = logic.symbolName(isOnline: true)

        XCTAssertEqual(result, "globe")
    }

    func testSymbolNameWhenOfflineIsWifiSlash() {
        let result = logic.symbolName(isOnline: false)

        XCTAssertEqual(result, "wifi.slash")
    }
}
