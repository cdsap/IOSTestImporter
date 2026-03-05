//
//  ContentView.swift
//  test1
//
//  Created by inaki villar on 2/22/26.
//

import SwiftUI

struct ContentView: View {
    private let logic = GreetingLogic()

    var body: some View {
        VStack {
            Image(systemName: logic.symbolName(isOnline: true))
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text(logic.greeting(name: nil))
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
