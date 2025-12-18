from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

#LRU CACHE IMPLEMENTATION
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> node

        # dummy head and tail
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        prev = node.prev
        nxt = node.next
        prev.next = nxt
        nxt.prev = prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.cache:
            return None
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
        elif len(self.cache) >= self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]

        node = Node(key, value)
        self.cache[key] = node
        self._add_to_front(node)

    def display(self):
        result = []
        curr = self.head.next
        while curr != self.tail:
            result.append({curr.key: curr.value})
            curr = curr.next
        return {
            "capacity": self.capacity,
            "current_size": len(self.cache),
            "cache": result
        }

# Initialize cache with capacity 3
lru_cache = LRUCache(3)

# ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/put", methods=["POST"])
def put_value():
    data = request.json
    if "key" not in data or "value" not in data:
        return jsonify({"error": "Key and value required"}), 400
    lru_cache.put(data["key"], data["value"])
    return jsonify(lru_cache.display())

@app.route("/get/<key>")
def get_value(key):
    value = lru_cache.get(key)
    if value is None:
        return jsonify({
            "error": "Key not found",
            "cache": lru_cache.display()
        }), 404
    return jsonify({"value": value, "cache": lru_cache.display()})

if __name__ == "__main__":
    app.run()
 