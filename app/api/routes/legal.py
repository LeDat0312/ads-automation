"""
Legal Pages - Privacy Policy and Terms of Service
Trang Chính sách quyền riêng tư và Điều khoản dịch vụ
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime

router = APIRouter(tags=["Legal"])


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    """Chính sách quyền riêng tư"""
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chính sách quyền riêng tư - Updatemetaads</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(to bottom, #020617, #0f172a);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }}
            
            .header {{
                width: 100%;
                padding: 24px 16px;
                max-width: 1280px;
                margin: 0 auto;
            }}
            
            .header-content {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 16px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            
            .logo-circle {{
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
            }}
            
            .logo-text {{
                color: white;
                font-weight: bold;
                font-size: 20px;
            }}
            
            .brand-info h1 {{
                font-size: 24px;
                font-weight: bold;
                color: white;
                margin-bottom: 4px;
            }}
            
            .brand-info p {{
                font-size: 14px;
                color: #94a3b8;
            }}
            
            .back-link {{
                color: #cbd5e1;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: color 0.2s;
            }}
            
            .back-link:hover {{
                color: white;
            }}
            
            .main-content {{
                max-width: 1024px;
                margin: 0 auto;
                padding: 32px 16px 64px;
            }}
            
            .content-card {{
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                background: rgba(15, 23, 42, 0.6);
                padding: 48px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            }}
            
            @media (max-width: 768px) {{
                .content-card {{
                    padding: 24px;
                }}
            }}
            
            .page-title {{
                font-size: 36px;
                font-weight: bold;
                color: white;
                margin-bottom: 16px;
            }}
            
            .page-subtitle {{
                color: #94a3b8;
                font-size: 18px;
                margin-bottom: 32px;
            }}
            
            .intro-text {{
                color: #cbd5e1;
                line-height: 1.75;
                margin-bottom: 32px;
            }}
            
            .section {{
                margin-bottom: 32px;
            }}
            
            .section-title {{
                font-size: 24px;
                font-weight: 600;
                color: white;
                margin-bottom: 16px;
            }}
            
            .section-content {{
                color: #cbd5e1;
                line-height: 1.75;
            }}
            
            .section-content p {{
                margin-bottom: 12px;
            }}
            
            .section-content ul {{
                list-style: disc;
                margin-left: 24px;
                margin-bottom: 12px;
            }}
            
            .section-content li {{
                margin-bottom: 8px;
            }}
            
            .section-content strong {{
                color: white;
                font-weight: 600;
            }}
            
            .highlight-box {{
                background: rgba(251, 191, 36, 0.1);
                border: 1px solid rgba(251, 191, 36, 0.3);
                border-radius: 12px;
                padding: 16px;
                margin-top: 16px;
            }}
            
            .highlight-box p {{
                color: #fbbf24;
                font-size: 14px;
                margin: 0;
            }}
            
            .info-box {{
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin-top: 16px;
            }}
            
            .info-box p {{
                color: white;
                font-weight: 500;
                margin-bottom: 8px;
            }}
            
            .info-box .info-text {{
                color: #94a3b8;
                font-size: 14px;
                margin: 0;
            }}
            
            .footer-note {{
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                color: #94a3b8;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-circle">
                        <span class="logo-text">UA</span>
                    </div>
                    <div class="brand-info">
                        <h1>Updatemetaads</h1>
                        <p>Nền tảng tự động hóa Facebook Ads</p>
                    </div>
                </div>
                <a href="/" class="back-link">
                    <span>←</span>
                    <span>Quay lại trang chủ</span>
                </a>
            </div>
        </header>
        
        <main class="main-content">
            <div class="content-card">
                <h1 class="page-title">Chính sách quyền riêng tư</h1>
                <p class="page-subtitle">Cập nhật lần cuối: {current_date}</p>
                
                <div class="intro-text">
                    Updatemetaads cung cấp nền tảng SaaS, thu thập dữ liệu từ Meta để hiển thị báo cáo và chạy automation. 
                    Chúng tôi cam kết bảo vệ quyền riêng tư và dữ liệu của bạn.
                </div>
                
                <section class="section">
                    <h2 class="section-title">1. Dữ liệu thu thập</h2>
                    <div class="section-content">
                        <p>Chúng tôi thu thập các loại dữ liệu sau để cung cấp dịch vụ:</p>
                        <ul>
                            <li><strong>Dữ liệu từ Meta API:</strong> Thông tin về chiến dịch quảng cáo, nhóm quảng cáo, quảng cáo, hiệu suất quảng cáo (chi tiêu, lượt hiển thị, lượt nhấp, chuyển đổi, v.v.)</li>
                            <li><strong>Thông tin tài khoản:</strong> Tên người dùng, email, cài đặt tài khoản và tùy chọn người dùng</li>
                            <li><strong>Token truy cập:</strong> Token Facebook/Meta được lưu trữ an toàn để kết nối với tài khoản quảng cáo của bạn</li>
                            <li><strong>Dữ liệu sử dụng:</strong> Log truy cập, thời gian sử dụng dịch vụ, và các hành động bạn thực hiện trên nền tảng</li>
                        </ul>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">2. Cách sử dụng dữ liệu</h2>
                    <div class="section-content">
                        <p>Chúng tôi sử dụng dữ liệu thu thập được cho các mục đích sau:</p>
                        <ul>
                            <li>Hiển thị báo cáo và phân tích hiệu suất quảng cáo</li>
                            <li>Chạy các automation và quy tắc tự động hóa theo cấu hình của bạn</li>
                            <li>Cải thiện và phát triển dịch vụ</li>
                            <li>Gửi thông báo và cập nhật về dịch vụ (nếu bạn đăng ký nhận)</li>
                            <li>Xử lý yêu cầu hỗ trợ và giải quyết vấn đề kỹ thuật</li>
                        </ul>
                        <div class="highlight-box">
                            <p><strong>⚠️ Lưu ý quan trọng:</strong> Chúng tôi KHÔNG bán, cho thuê, hoặc chia sẻ dữ liệu của bạn với bên thứ ba vì mục đích quảng cáo hoặc marketing.</p>
                        </div>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">3. Cam kết bảo mật và chia sẻ dữ liệu</h2>
                    <div class="section-content">
                        <p>Chúng tôi cam kết chỉ sử dụng dữ liệu của bạn để cung cấp dịch vụ và không chia sẻ với bên thứ ba, trừ các trường hợp sau:</p>
                        <ul>
                            <li><strong>Nhà cung cấp dịch vụ:</strong> Chúng tôi có thể sử dụng các nhà cung cấp dịch vụ đáng tin cậy (như dịch vụ lưu trữ đám mây) để vận hành nền tảng, nhưng họ chỉ được phép xử lý dữ liệu theo hướng dẫn của chúng tôi</li>
                            <li><strong>Yêu cầu pháp lý:</strong> Chúng tôi có thể tiết lộ dữ liệu nếu được yêu cầu bởi cơ quan pháp luật hoặc để tuân thủ các quy định pháp lý</li>
                            <li><strong>Bảo vệ quyền lợi:</strong> Chúng tôi có thể tiết lộ thông tin để bảo vệ quyền, tài sản hoặc an toàn của chúng tôi, người dùng hoặc người khác</li>
                        </ul>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">4. Bảo mật & lưu trữ</h2>
                    <div class="section-content">
                        <p>Chúng tôi áp dụng các biện pháp bảo mật sau để bảo vệ dữ liệu của bạn:</p>
                        <ul>
                            <li>Mã hóa dữ liệu trong quá trình truyền (HTTPS/TLS)</li>
                            <li>Mã hóa token và thông tin nhạy cảm khi lưu trữ</li>
                            <li>Kiểm soát truy cập nghiêm ngặt và xác thực người dùng</li>
                            <li>Giám sát và phát hiện các hoạt động bất thường</li>
                            <li>Sao lưu dữ liệu định kỳ để đảm bảo tính khả dụng</li>
                        </ul>
                        <p style="margin-top: 16px;">Dữ liệu được lưu trữ trên các máy chủ an toàn và chỉ được giữ lại trong thời gian cần thiết để cung cấp dịch vụ hoặc theo yêu cầu pháp lý.</p>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">5. Quyền của bạn</h2>
                    <div class="section-content">
                        <p>Bạn có các quyền sau đối với dữ liệu của mình:</p>
                        <ul>
                            <li><strong>Quyền truy cập:</strong> Bạn có thể xem và xuất dữ liệu của mình thông qua giao diện nền tảng</li>
                            <li><strong>Quyền chỉnh sửa:</strong> Bạn có thể cập nhật thông tin tài khoản và cài đặt của mình</li>
                            <li><strong>Quyền xóa:</strong> Bạn có thể yêu cầu xóa tài khoản và dữ liệu của mình (một số dữ liệu có thể được giữ lại để tuân thủ pháp luật)</li>
                            <li><strong>Quyền ngắt kết nối:</strong> Bạn có thể ngắt kết nối ứng dụng Updatemetaads khỏi tài khoản Facebook của mình bất cứ lúc nào thông qua <strong>Facebook Business Settings</strong></li>
                            <li><strong>Quyền từ chối:</strong> Bạn có thể từ chối việc thu thập một số dữ liệu nhất định, nhưng điều này có thể ảnh hưởng đến chức năng của dịch vụ</li>
                        </ul>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">6. Thông tin liên hệ</h2>
                    <div class="section-content">
                        <p>Nếu bạn có câu hỏi, yêu cầu hoặc khiếu nại về chính sách quyền riêng tư này, vui lòng liên hệ với chúng tôi:</p>
                        <div class="info-box">
                            <p>Updatemetaads</p>
                            <p class="info-text">Email: support@updatemetaads.com</p>
                            <p class="info-text" style="margin-top: 8px;">Thời gian phản hồi: Chúng tôi sẽ phản hồi trong vòng 48 giờ làm việc.</p>
                        </div>
                    </div>
                </section>
                
                <div class="footer-note">
                    Chúng tôi có thể cập nhật chính sách này theo thời gian. Mọi thay đổi sẽ được thông báo trên trang này.
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/terms", response_class=HTMLResponse)
async def terms_page():
    """Điều khoản dịch vụ"""
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Điều khoản dịch vụ - Updatemetaads</title>
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(to bottom, #020617, #0f172a);
                min-height: 100vh;
                color: #e2e8f0;
                line-height: 1.6;
            }}
            
            .header {{
                width: 100%;
                padding: 24px 16px;
                max-width: 1280px;
                margin: 0 auto;
            }}
            
            .header-content {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 16px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            
            .logo-circle {{
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
            }}
            
            .logo-text {{
                color: white;
                font-weight: bold;
                font-size: 20px;
            }}
            
            .brand-info h1 {{
                font-size: 24px;
                font-weight: bold;
                color: white;
                margin-bottom: 4px;
            }}
            
            .brand-info p {{
                font-size: 14px;
                color: #94a3b8;
            }}
            
            .back-link {{
                color: #cbd5e1;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: color 0.2s;
            }}
            
            .back-link:hover {{
                color: white;
            }}
            
            .main-content {{
                max-width: 1024px;
                margin: 0 auto;
                padding: 32px 16px 64px;
            }}
            
            .content-card {{
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                background: rgba(15, 23, 42, 0.6);
                padding: 48px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            }}
            
            @media (max-width: 768px) {{
                .content-card {{
                    padding: 24px;
                }}
            }}
            
            .page-title {{
                font-size: 36px;
                font-weight: bold;
                color: white;
                margin-bottom: 16px;
            }}
            
            .page-subtitle {{
                color: #94a3b8;
                font-size: 18px;
                margin-bottom: 32px;
            }}
            
            .intro-text {{
                color: #cbd5e1;
                line-height: 1.75;
                margin-bottom: 32px;
            }}
            
            .section {{
                margin-bottom: 32px;
            }}
            
            .section-title {{
                font-size: 24px;
                font-weight: 600;
                color: white;
                margin-bottom: 16px;
            }}
            
            .section-content {{
                color: #cbd5e1;
                line-height: 1.75;
            }}
            
            .section-content p {{
                margin-bottom: 12px;
            }}
            
            .section-content ul {{
                list-style: disc;
                margin-left: 24px;
                margin-bottom: 12px;
            }}
            
            .section-content li {{
                margin-bottom: 8px;
            }}
            
            .section-content strong {{
                color: white;
                font-weight: 600;
            }}
            
            .warning-box {{
                background: rgba(251, 191, 36, 0.1);
                border: 1px solid rgba(251, 191, 36, 0.3);
                border-radius: 12px;
                padding: 16px;
                margin-top: 16px;
            }}
            
            .warning-box p {{
                color: #fbbf24;
                font-size: 14px;
                margin: 0;
            }}
            
            .info-box {{
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin-top: 16px;
            }}
            
            .info-box p {{
                color: white;
                font-weight: 500;
                margin-bottom: 8px;
            }}
            
            .info-box .info-text {{
                color: #94a3b8;
                font-size: 14px;
                margin: 0;
            }}
            
            .footer-note {{
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                color: #94a3b8;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-circle">
                        <span class="logo-text">UA</span>
                    </div>
                    <div class="brand-info">
                        <h1>Updatemetaads</h1>
                        <p>Nền tảng tự động hóa Facebook Ads</p>
                    </div>
                </div>
                <a href="/" class="back-link">
                    <span>←</span>
                    <span>Quay lại trang chủ</span>
                </a>
            </div>
        </header>
        
        <main class="main-content">
            <div class="content-card">
                <h1 class="page-title">Điều khoản dịch vụ</h1>
                <p class="page-subtitle">Cập nhật lần cuối: {current_date}</p>
                
                <div class="intro-text">
                    Bằng việc sử dụng nền tảng Updatemetaads, bạn đồng ý với các điều khoản dịch vụ sau đây. 
                    Vui lòng đọc kỹ trước khi sử dụng dịch vụ.
                </div>
                
                <section class="section">
                    <h2 class="section-title">1. Mô tả dịch vụ</h2>
                    <div class="section-content">
                        <p>Updatemetaads là nền tảng SaaS (Software as a Service) cung cấp các công cụ tự động hóa và quản lý quảng cáo Facebook Ads. Dịch vụ bao gồm:</p>
                        <ul>
                            <li>Hiển thị báo cáo và phân tích hiệu suất quảng cáo từ Meta API</li>
                            <li>Tự động hóa các thao tác quản lý quảng cáo (điều chỉnh ngân sách, bật/tắt quảng cáo, v.v.)</li>
                            <li>Quản lý và theo dõi nhiều tài khoản quảng cáo</li>
                            <li>Các tính năng automation và quy tắc tự động theo cấu hình của người dùng</li>
                        </ul>
                        <p style="margin-top: 16px;">Chúng tôi cung cấp dịch vụ "như hiện tại" và có thể thay đổi, tạm ngưng hoặc ngừng bất kỳ tính năng nào mà không cần thông báo trước.</p>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">2. Trách nhiệm người dùng</h2>
                    <div class="section-content">
                        <p>Khi sử dụng dịch vụ, bạn có trách nhiệm:</p>
                        <ul>
                            <li><strong>Bảo mật tài khoản:</strong> Bạn chịu trách nhiệm bảo vệ thông tin đăng nhập và token truy cập của mình. Không chia sẻ thông tin đăng nhập với người khác.</li>
                            <li><strong>Nội dung quảng cáo:</strong> Bạn chịu trách nhiệm hoàn toàn về nội dung quảng cáo được tạo, chỉnh sửa hoặc quản lý thông qua nền tảng. Chúng tôi không chịu trách nhiệm về vi phạm chính sách quảng cáo của Facebook/Meta.</li>
                            <li><strong>Tuân thủ quy định:</strong> Bạn phải tuân thủ tất cả các quy định, chính sách và điều khoản của Facebook/Meta, cũng như các luật pháp hiện hành liên quan đến quảng cáo và tiếp thị.</li>
                            <li><strong>Sử dụng hợp pháp:</strong> Bạn cam kết không sử dụng dịch vụ cho các mục đích bất hợp pháp, gian lận, hoặc vi phạm quyền của người khác.</li>
                            <li><strong>Cấu hình automation:</strong> Bạn chịu trách nhiệm về các quy tắc và cấu hình automation mà bạn thiết lập. Chúng tôi không chịu trách nhiệm về các thay đổi không mong muốn do automation của bạn gây ra.</li>
                            <li><strong>Báo cáo sự cố:</strong> Bạn nên báo cáo ngay lập tức nếu phát hiện bất kỳ hoạt động bất thường hoặc vi phạm bảo mật nào.</li>
                        </ul>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">3. Trách nhiệm của chúng tôi</h2>
                    <div class="section-content">
                        <p>Chúng tôi cam kết:</p>
                        <ul>
                            <li><strong>Cung cấp dịch vụ:</strong> Cung cấp dịch vụ với mức độ khả dụng cao nhất có thể và nỗ lực duy trì hoạt động ổn định</li>
                            <li><strong>Bảo mật dữ liệu:</strong> Áp dụng các biện pháp bảo mật phù hợp để bảo vệ dữ liệu của bạn (xem thêm Chính sách quyền riêng tư)</li>
                            <li><strong>Hỗ trợ kỹ thuật:</strong> Cung cấp hỗ trợ kỹ thuật và giải đáp thắc mắc trong khả năng của chúng tôi</li>
                            <li><strong>Cải thiện dịch vụ:</strong> Liên tục cải thiện và phát triển các tính năng của nền tảng</li>
                        </ul>
                        <div class="warning-box">
                            <p><strong>Giới hạn trách nhiệm:</strong> Chúng tôi không đảm bảo rằng dịch vụ sẽ hoàn toàn không có lỗi, không bị gián đoạn, hoặc đáp ứng mọi yêu cầu của bạn. Chúng tôi không chịu trách nhiệm về bất kỳ thiệt hại trực tiếp, gián tiếp, ngẫu nhiên hoặc hậu quả nào phát sinh từ việc sử dụng dịch vụ.</p>
                        </div>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">4. Quyền ngắt kết nối / chấm dứt</h2>
                    <div class="section-content">
                        <p><strong>Ngắt kết nối từ phía bạn:</strong></p>
                        <ul>
                            <li>Bạn có thể ngắt kết nối ứng dụng Updatemetaads khỏi tài khoản Facebook của mình bất cứ lúc nào thông qua <strong>Facebook Business Settings</strong> → Apps → Updatemetaads → Remove</li>
                            <li>Bạn có thể yêu cầu xóa tài khoản và dữ liệu của mình bằng cách liên hệ với chúng tôi</li>
                            <li>Sau khi ngắt kết nối, chúng tôi sẽ ngừng thu thập dữ liệu mới từ tài khoản của bạn, nhưng có thể giữ lại một số dữ liệu để tuân thủ pháp luật hoặc giải quyết tranh chấp</li>
                        </ul>
                        <p style="margin-top: 16px;"><strong>Chấm dứt từ phía chúng tôi:</strong></p>
                        <ul>
                            <li>Chúng tôi có quyền tạm ngưng hoặc chấm dứt quyền truy cập của bạn nếu bạn vi phạm các điều khoản này, sử dụng dịch vụ bất hợp pháp, hoặc có hành vi gây hại đến dịch vụ hoặc người dùng khác</li>
                            <li>Chúng tôi sẽ thông báo trước (nếu có thể) trước khi chấm dứt tài khoản của bạn, trừ trường hợp vi phạm nghiêm trọng</li>
                        </ul>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">5. Thay đổi điều khoản</h2>
                    <div class="section-content">
                        <p>Chúng tôi có quyền cập nhật hoặc thay đổi các điều khoản dịch vụ này bất cứ lúc nào. Các thay đổi sẽ có hiệu lực ngay sau khi được đăng tải trên trang này.</p>
                        <p>Việc bạn tiếp tục sử dụng dịch vụ sau khi các điều khoản được cập nhật được coi là bạn đã chấp nhận các thay đổi đó.</p>
                        <p>Chúng tôi khuyến nghị bạn thường xuyên xem lại các điều khoản này để cập nhật các thay đổi mới nhất.</p>
                    </div>
                </section>
                
                <section class="section">
                    <h2 class="section-title">6. Thông tin liên hệ</h2>
                    <div class="section-content">
                        <p>Nếu bạn có câu hỏi, yêu cầu hoặc khiếu nại về các điều khoản dịch vụ này, vui lòng liên hệ với chúng tôi:</p>
                        <div class="info-box">
                            <p>Updatemetaads</p>
                            <p class="info-text">Email: support@updatemetaads.com</p>
                            <p class="info-text" style="margin-top: 8px;">Thời gian phản hồi: Chúng tôi sẽ phản hồi trong vòng 48 giờ làm việc.</p>
                        </div>
                    </div>
                </section>
                
                <div class="footer-note">
                    Bằng việc sử dụng dịch vụ Updatemetaads, bạn xác nhận rằng bạn đã đọc, hiểu và đồng ý với tất cả các điều khoản trên.
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

