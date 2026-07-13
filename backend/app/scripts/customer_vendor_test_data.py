import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_bulk_logins():
    print("Testing 50 vendor logins...")
    success = 0
    fail = 0
    start = time.time()

    for i in range(1, 51):
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": f"vendor{i}@loadtest.com",
            "password": "Test@1234"
        })
        if response.status_code == 200:
            success += 1
        else:
            fail += 1
            print(f"  ❌ vendor{i} login failed: {response.status_code}")

    elapsed = time.time() - start
    print(f"✅ {success} succeeded, ❌ {fail} failed, took {elapsed:.2f}s")


def test_bulk_customer_logins():
    print("\nTesting 100 customer logins...")
    success = 0
    fail = 0
    start = time.time()

    for i in range(1, 101):
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": f"customer{i}@loadtest.com",
            "password": "Test@1234"
        })
        if response.status_code == 200:
            success += 1
        else:
            fail += 1

    elapsed = time.time() - start
    print(f"✅ {success} succeeded, ❌ {fail} failed, took {elapsed:.2f}s")


def test_vendor_listing_performance():
    print("\nTesting vendor list endpoint performance...")
    times = []
    for _ in range(10):
        start = time.time()
        response = requests.get(f"{BASE_URL}/vendors?limit=20")
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    print(f"Average response time over 10 calls: {avg_time*1000:.0f}ms")
    if avg_time > 0.5:
        print("⚠️  Response time exceeds 500ms — consider adding database indexes")
    else:
        print("✅ Performance acceptable")


def test_pagination_completeness():
    print("\nTesting pagination returns all vendors without gaps/duplicates...")
    all_ids = set()
    skip = 0
    limit = 10

    while True:
        response = requests.get(f"{BASE_URL}/vendors?skip={skip}&limit={limit}")
        data = response.json()
        if not data:
            break
        for v in data:
            if v['id'] in all_ids:
                print(f"⚠️  Duplicate vendor ID {v['id']} found across pages!")
            all_ids.add(v['id'])
        skip += limit

    print(f"✅ Total unique vendors retrieved via pagination: {len(all_ids)}")


if __name__ == "__main__":
    test_bulk_logins()
    test_bulk_customer_logins()
    test_vendor_listing_performance()
    test_pagination_completeness()