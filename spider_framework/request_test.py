import requests

a = requests.get("https://images.unsplash.com/photo-1540809634-b8d976ccdaa5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MXwxMjA3fDB8MXx0b3BpY3x8R3RyQlNjdjFiNU18fHx8fDJ8&ixlib=rb-1.2.1&q=80&w=1080")

print(type(a), a.__dict__)