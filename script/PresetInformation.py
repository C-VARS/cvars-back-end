Alex = {
    "userType": "Driver",
    "username": "Alex",
    "password": "alex12345",
    "contact": "2938578",
    "name": "Alexander Yang",
}

Callum = {
    "userType": "Driver",
    "username": "Callum",
    "password": "callum12345",
    "contact": "4938279",
    "name": "Callum Cassidy Nolan",
}

Raag = {
    "userType": "Customer",
    "username": "Raag",
    "password": "raag12345",
    "contact": "29039459",
    "name": "Raag Kashyap",
    "bankInformation": "ScotiaRaag",
    "address": "123 Business Street"
}

Vlad = {
    "userType": "Customer",
    "username": "Vlad",
    "password": "vlad12345",
    "contact": "2340499",
    "name": "Vladimir Dyagilev",
    "bankInformation": "ScotiaVlad",
    "address": "200 Business Street"
}

Sophie = {
    "userType": "Supplier",
    "username": "Sophie",
    "password": "sophie12345",
    "contact": "13469868",
    "name": "Sophie's Cola",
    "bankInformation": "ScotiaSophieCola",
    "address": "990 Business Street"
}

invoice_one = {
    "customerUsername": "Raag",
    "supplierUsername": "Sophie",
    "driverUsername": "Alex",
    "orders": [{
        "item": "Normal Coke",
        "price": 2.5,
        "amount": 3
    },
        {
            "item": "Huge Coke",
            "price": 200,
            "amount": 3
        }
    ]
}

invoice_two = {
    "customerUsername": "Vlad",
    "supplierUsername": "Sophie",
    "driverUsername": "Callum",
    "orders": [{
        "item": "Cherry Coke",
        "price": 5.5,
        "amount": 10
    },
        {
            "item": "Illegal Coke",
            "price": 20000,
            "amount": 1
        }
    ]
}
