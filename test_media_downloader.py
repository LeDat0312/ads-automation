"""
Test script cho Media Downloader
Chạy script này để test download media từ Facebook Ads
"""
import asyncio
import httpx

# API endpoints
BASE_URL = "http://localhost:8000"  # Hoặc URL của server
API_TOKEN = "your_auth_token_here"  # Replace với token thật

async def test_download_single_ad():
    """Test download media của 1 ad"""
    print("=" * 60)
    print("TEST 1: Download media của một ad")
    print("=" * 60)
    
    payload = {
        "ad_id": "test_ad_123",
        "ad_image_url": "https://scontent.xx.fbcdn.net/v/t45.1600-4/your_image_url.jpg",
        "ad_video_url": None,  # Optional
        "page_name": "Test Competitor",
        "force_redownload": False
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/competitor/media/download",
            json=payload,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Response: {result}")
        
        if result.get("success"):
            if result.get("image"):
                print(f"\n✅ Image downloaded:")
                print(f"  - Path: {result['image']['path']}")
                print(f"  - Size: {result['image']['size_mb']} MB")
            if result.get("video"):
                print(f"\n✅ Video downloaded:")
                print(f"  - Path: {result['video']['path']}")
                print(f"  - Size: {result['video']['size_mb']} MB")
        else:
            print(f"\n❌ Download failed: {result.get('message')}")


async def test_batch_download():
    """Test batch download nhiều ads"""
    print("\n" + "=" * 60)
    print("TEST 2: Batch download nhiều ads")
    print("=" * 60)
    
    # Giả sử bạn đã scrape được list ads này
    ads = [
        {
            "ad_id": "ad_001",
            "ad_image_url": "https://scontent.xx.fbcdn.net/v/t45.1600-4/image1.jpg",
            "page_name": "Competitor A"
        },
        {
            "ad_id": "ad_002",
            "ad_image_url": "https://scontent.xx.fbcdn.net/v/t45.1600-4/image2.jpg",
            "ad_video_url": "https://video.xx.fbcdn.net/v/t42.1790-2/video.mp4",
            "page_name": "Competitor B"
        },
        {
            "ad_id": "ad_003",
            "ad_image_url": "https://scontent.xx.fbcdn.net/v/t45.1600-4/image3.jpg",
            "page_name": "Competitor A"
        }
    ]
    
    payload = {
        "ads": ads,
        "concurrent_limit": 3  # Download 3 cùng lúc
    }
    
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{BASE_URL}/competitor/media/batch-download",
            json=payload,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"\n✅ Downloaded: {result.get('downloaded')}/{result.get('total_ads')} ads")
        
        for item in result.get('results', []):
            ad_id = item.get('ad_id')
            has_image = item.get('image') is not None
            has_video = item.get('video') is not None
            print(f"  - {ad_id}: Image={has_image}, Video={has_video}")


async def test_get_storage_stats():
    """Test lấy storage stats"""
    print("\n" + "=" * 60)
    print("TEST 3: Get storage statistics")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/competitor/media/storage-stats",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        result = response.json()
        if result.get("success"):
            stats = result.get("stats", {})
            print(f"\n📊 Storage Statistics:")
            print(f"  - Total Images: {stats.get('total_images')}")
            print(f"  - Total Videos: {stats.get('total_videos')}")
            print(f"  - Total Files: {stats.get('total_files')}")
            print(f"  - Total Size: {stats.get('total_size_mb')} MB")
            print(f"  - Storage Path: {stats.get('storage_path')}")


async def test_get_media_file():
    """Test lấy file đã download"""
    print("\n" + "=" * 60)
    print("TEST 4: Get downloaded media file")
    print("=" * 60)
    
    ad_id = "test_ad_123"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/competitor/media/file/{ad_id}?media_type=image",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        if response.status_code == 200:
            # File được return
            print(f"\n✅ File found for ad {ad_id}")
            print(f"  - Content-Type: {response.headers.get('content-type')}")
            print(f"  - Content-Length: {len(response.content)} bytes")
            
            # Có thể save file
            # with open(f"downloaded_{ad_id}.jpg", "wb") as f:
            #     f.write(response.content)
        else:
            print(f"\n❌ File not found: {response.json().get('detail')}")


async def demo_workflow():
    """Demo workflow hoàn chỉnh"""
    print("\n" + "=" * 60)
    print("DEMO: Complete Workflow")
    print("=" * 60)
    
    # Step 1: Scrape ads từ competitor
    print("\n1️⃣ Scraping competitor ads...")
    
    competitor_payload = {
        "page_id": "123456789",  # Facebook Page ID
        "limit": 10,
        "use_cache": True
    }
    
    async with httpx.AsyncClient(timeout=120) as client:
        # Scrape competitor ads
        scrape_response = await client.post(
            f"{BASE_URL}/competitor/scrape/competitor",
            json=competitor_payload,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        scrape_result = scrape_response.json()
        
        if not scrape_result.get("success"):
            print(f"❌ Scraping failed: {scrape_result.get('message')}")
            return
        
        ads = scrape_result.get("data", [])
        print(f"✅ Found {len(ads)} ads")
        
        # Step 2: Auto-download media cho tất cả ads
        print("\n2️⃣ Downloading media for all ads...")
        
        download_payload = {
            "ads": [
                {
                    "ad_id": ad["ad_id"],
                    "ad_image_url": ad.get("ad_image_url"),
                    "ad_video_url": ad.get("ad_video_url"),
                    "page_name": ad.get("page_name", "unknown")
                }
                for ad in ads
            ],
            "concurrent_limit": 5
        }
        
        download_response = await client.post(
            f"{BASE_URL}/competitor/media/batch-download",
            json=download_payload,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        download_result = download_response.json()
        print(f"✅ Downloaded: {download_result.get('downloaded')}/{len(ads)} ads")
        
        # Step 3: Check storage stats
        print("\n3️⃣ Checking storage...")
        
        stats_response = await client.get(
            f"{BASE_URL}/competitor/media/storage-stats",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        stats_result = stats_response.json()
        if stats_result.get("success"):
            stats = stats_result["stats"]
            print(f"📊 Total stored: {stats['total_files']} files ({stats['total_size_mb']} MB)")
        
        print("\n✅ Workflow completed!")


async def main():
    """Run all tests"""
    print("\n" + "🚀 " * 30)
    print("FACEBOOK ADS MEDIA DOWNLOADER - TEST SUITE")
    print("🚀 " * 30)
    
    # Uncomment tests bạn muốn chạy:
    
    # await test_download_single_ad()
    # await test_batch_download()
    # await test_get_storage_stats()
    # await test_get_media_file()
    await demo_workflow()
    
    print("\n" + "✅ " * 30)
    print("ALL TESTS COMPLETED")
    print("✅ " * 30 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
