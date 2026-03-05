import Foundation

struct GreetingLogic {
    func greeting(name: String?) -> String {
        guard let trimmedName = name?.trimmingCharacters(in: .whitespacesAndNewlines),
              !trimmedName.isEmpty else {
            return "Hello, world!"
        }

        return "Hello, \(trimmedName)!"
    }

    func symbolName(isOnline: Bool) -> String {
        isOnline ? "globe" : "wifi.slash"
    }
}
