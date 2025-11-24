import React from 'react';
import { Link } from 'react-router-dom';

const TermsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="w-full px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo UA in circle */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">UA</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Updatemetaads</h1>
              <p className="text-sm text-slate-400">Nền tảng tự động hóa Facebook Ads</p>
            </div>
          </div>
          <Link
            to="/"
            className="text-slate-300 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium"
          >
            <span>←</span>
            <span>Quay lại trang chủ</span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-16">
        <div className="rounded-3xl border border-white/5 bg-slate-900/60 p-6 sm:p-8 md:p-12 shadow-xl shadow-black/40">
          {/* Title */}
          <h1 className="text-4xl font-bold text-white mb-4">Điều khoản dịch vụ</h1>
          <p className="text-slate-400 text-lg mb-8">Cập nhật lần cuối: {new Date().toLocaleDateString('vi-VN')}</p>

          {/* Introduction */}
          <div className="mb-8">
            <p className="text-slate-300 leading-relaxed text-base">
              Bằng việc sử dụng nền tảng Updatemetaads, bạn đồng ý với các điều khoản dịch vụ sau đây. 
              Vui lòng đọc kỹ trước khi sử dụng dịch vụ.
            </p>
          </div>

          {/* Section 1: Mô tả dịch vụ */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">1. Mô tả dịch vụ</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                Updatemetaads là nền tảng SaaS (Software as a Service) cung cấp các công cụ tự động hóa 
                và quản lý quảng cáo Facebook Ads. Dịch vụ bao gồm:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Hiển thị báo cáo và phân tích hiệu suất quảng cáo từ Meta API</li>
                <li>Tự động hóa các thao tác quản lý quảng cáo (điều chỉnh ngân sách, bật/tắt quảng cáo, v.v.)</li>
                <li>Quản lý và theo dõi nhiều tài khoản quảng cáo</li>
                <li>Các tính năng automation và quy tắc tự động theo cấu hình của người dùng</li>
              </ul>
              <p className="mt-4">
                Chúng tôi cung cấp dịch vụ "như hiện tại" và có thể thay đổi, tạm ngưng hoặc ngừng 
                bất kỳ tính năng nào mà không cần thông báo trước.
              </p>
            </div>
          </section>

          {/* Section 2: Trách nhiệm người dùng */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">2. Trách nhiệm người dùng</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>Khi sử dụng dịch vụ, bạn có trách nhiệm:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong className="text-white">Bảo mật tài khoản:</strong> Bạn chịu trách nhiệm bảo vệ 
                  thông tin đăng nhập và token truy cập của mình. Không chia sẻ thông tin đăng nhập với người khác.
                </li>
                <li>
                  <strong className="text-white">Nội dung quảng cáo:</strong> Bạn chịu trách nhiệm hoàn toàn về 
                  nội dung quảng cáo được tạo, chỉnh sửa hoặc quản lý thông qua nền tảng. Chúng tôi không chịu 
                  trách nhiệm về vi phạm chính sách quảng cáo của Facebook/Meta.
                </li>
                <li>
                  <strong className="text-white">Tuân thủ quy định:</strong> Bạn phải tuân thủ tất cả các quy định, 
                  chính sách và điều khoản của Facebook/Meta, cũng như các luật pháp hiện hành liên quan đến 
                  quảng cáo và tiếp thị.
                </li>
                <li>
                  <strong className="text-white">Sử dụng hợp pháp:</strong> Bạn cam kết không sử dụng dịch vụ 
                  cho các mục đích bất hợp pháp, gian lận, hoặc vi phạm quyền của người khác.
                </li>
                <li>
                  <strong className="text-white">Cấu hình automation:</strong> Bạn chịu trách nhiệm về các quy tắc 
                  và cấu hình automation mà bạn thiết lập. Chúng tôi không chịu trách nhiệm về các thay đổi không 
                  mong muốn do automation của bạn gây ra.
                </li>
                <li>
                  <strong className="text-white">Báo cáo sự cố:</strong> Bạn nên báo cáo ngay lập tức nếu phát hiện 
                  bất kỳ hoạt động bất thường hoặc vi phạm bảo mật nào.
                </li>
              </ul>
            </div>
          </section>

          {/* Section 3: Trách nhiệm của chúng tôi */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">3. Trách nhiệm của chúng tôi</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>Chúng tôi cam kết:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong className="text-white">Cung cấp dịch vụ:</strong> Cung cấp dịch vụ với mức độ khả dụng 
                  cao nhất có thể và nỗ lực duy trì hoạt động ổn định
                </li>
                <li>
                  <strong className="text-white">Bảo mật dữ liệu:</strong> Áp dụng các biện pháp bảo mật phù hợp 
                  để bảo vệ dữ liệu của bạn (xem thêm Chính sách quyền riêng tư)
                </li>
                <li>
                  <strong className="text-white">Hỗ trợ kỹ thuật:</strong> Cung cấp hỗ trợ kỹ thuật và giải đáp 
                  thắc mắc trong khả năng của chúng tôi
                </li>
                <li>
                  <strong className="text-white">Cải thiện dịch vụ:</strong> Liên tục cải thiện và phát triển 
                  các tính năng của nền tảng
                </li>
              </ul>
              <div className="bg-amber-900/20 border border-amber-700/50 rounded-lg p-4 mt-4">
                <p className="text-amber-200 text-sm">
                  <strong>Giới hạn trách nhiệm:</strong> Chúng tôi không đảm bảo rằng dịch vụ sẽ hoàn toàn không có lỗi, 
                  không bị gián đoạn, hoặc đáp ứng mọi yêu cầu của bạn. Chúng tôi không chịu trách nhiệm về bất kỳ 
                  thiệt hại trực tiếp, gián tiếp, ngẫu nhiên hoặc hậu quả nào phát sinh từ việc sử dụng dịch vụ.
                </p>
              </div>
            </div>
          </section>

          {/* Section 4: Quyền ngắt kết nối / chấm dứt */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">4. Quyền ngắt kết nối / chấm dứt</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                <strong className="text-white">Ngắt kết nối từ phía bạn:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  Bạn có thể ngắt kết nối ứng dụng Updatemetaads khỏi tài khoản Facebook của mình bất cứ lúc nào 
                  thông qua <strong className="text-white">Facebook Business Settings</strong> → Apps → 
                  Updatemetaads → Remove
                </li>
                <li>
                  Bạn có thể yêu cầu xóa tài khoản và dữ liệu của mình bằng cách liên hệ với chúng tôi
                </li>
                <li>
                  Sau khi ngắt kết nối, chúng tôi sẽ ngừng thu thập dữ liệu mới từ tài khoản của bạn, 
                  nhưng có thể giữ lại một số dữ liệu để tuân thủ pháp luật hoặc giải quyết tranh chấp
                </li>
              </ul>
              <p className="mt-4">
                <strong className="text-white">Chấm dứt từ phía chúng tôi:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  Chúng tôi có quyền tạm ngưng hoặc chấm dứt quyền truy cập của bạn nếu bạn vi phạm các điều khoản này, 
                  sử dụng dịch vụ bất hợp pháp, hoặc có hành vi gây hại đến dịch vụ hoặc người dùng khác
                </li>
                <li>
                  Chúng tôi sẽ thông báo trước (nếu có thể) trước khi chấm dứt tài khoản của bạn, 
                  trừ trường hợp vi phạm nghiêm trọng
                </li>
              </ul>
            </div>
          </section>

          {/* Section 5: Thay đổi điều khoản */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">5. Thay đổi điều khoản</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                Chúng tôi có quyền cập nhật hoặc thay đổi các điều khoản dịch vụ này bất cứ lúc nào. 
                Các thay đổi sẽ có hiệu lực ngay sau khi được đăng tải trên trang này.
              </p>
              <p>
                Việc bạn tiếp tục sử dụng dịch vụ sau khi các điều khoản được cập nhật được coi là 
                bạn đã chấp nhận các thay đổi đó.
              </p>
              <p>
                Chúng tôi khuyến nghị bạn thường xuyên xem lại các điều khoản này để cập nhật 
                các thay đổi mới nhất.
              </p>
            </div>
          </section>

          {/* Section 6: Thông tin liên hệ */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">6. Thông tin liên hệ</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                Nếu bạn có câu hỏi, yêu cầu hoặc khiếu nại về các điều khoản dịch vụ này, 
                vui lòng liên hệ với chúng tôi:
              </p>
              <div className="bg-slate-800/50 rounded-lg p-4 mt-4 border border-slate-700/50">
                <p className="text-white font-medium mb-2">Updatemetaads</p>
                <p className="text-sm">Email: support@updatemetaads.com</p>
                <p className="text-sm mt-1">
                  Thời gian phản hồi: Chúng tôi sẽ phản hồi trong vòng 48 giờ làm việc.
                </p>
              </div>
            </div>
          </section>

          {/* Footer note */}
          <div className="mt-8 pt-6 border-t border-slate-700/50">
            <p className="text-sm text-slate-400 text-center">
              Bằng việc sử dụng dịch vụ Updatemetaads, bạn xác nhận rằng bạn đã đọc, hiểu và đồng ý 
              với tất cả các điều khoản trên.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TermsPage;

