# check if a dictionary can be used as a key in another dict.
k = {"a": 1, "b": 2}
d = {k: "a1b2"} # no.

# petname instead of UID
from petname import generate
generate(3)

# check if two lists are equal
[1] == [1]

# check petname
import numpy as np
from petname import adjectives, adverbs, names

def number_at_confidence(count, confidence):
    # p = (1 - 1/count)^(n-1)
    # ln p/ln((count - 1)/count) = n
    return np.log(confidence)/(np.log(count-1) - np.log(count))

def probability_of_clash(count, draws):
    # p = (1 - 1/count)^(n-1)
    # ln p/ln((count - 1)/count) = n
    return 1 - np.exp((draws-1)*(np.log(count-1) - np.log(count)))

print(f"Number of adverbs: {len(adverbs)}")
print(f"Number of adjectives: {len(adjectives)}")
print(f"Number of names: {len(names)}")

probabilityAllUnique = 0.999999
for nadv in range(4):
    label = '-'.join(nadv*['adverb'] + ['adjective', 'name'])
    count = len(adverbs)**nadv * len(adjectives) * len(names)
    print(f"{label}: {count:,} ({int(np.log2(count))} bits)")
    # p = (1 - 1/count)^(n-1)
    # ln p/ln((count - 1)/count) = n
    nUnique = np.log(probabilityAllUnique)/(np.log(count-1) - np.log(count))
    print(f"{int(nUnique):,} unique with {100*probabilityAllUnique}% confidence")
    print("--")

number_at_confidence(205184, 0.999)
probability_of_clash(205184, 207)

# json serialization
import json

class Foo:
    def __init__(self):
        self.__key = "private"

    def tojson(self):
        return {"key": self._key}

foo = Foo()
json.dumps(foo, default=lambda o: o.__dict__)

class Bar(Foo, list):
    def __init__(self, *args, **kwds):
        Foo.__init__(self)
        list.__init__(self, *args, **kwds)

    def tojson(self):
        rval = Foo.tojson(self)
        rval["contents"] = json.JSONEncoder().default(self)
        return rval

bar = Bar()
bar.extend(range(5))
bar
bar.__dict__
json.dumps(bar, default=lambda o: o.__dict__)

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if "tojson" in dir(o):
            return o.tojson()
        return json.JSONEncoder.default(self, o)

json.dumps(bar, cls=CustomEncoder)
bar.tojson()
