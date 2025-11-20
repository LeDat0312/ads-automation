// File: Pages.gs
// === Quản lý Fanpage ===

/**
 * Liệt kê các Fanpage mà token hiện tại quản lý (quyền admin)
 * Đọc ACCESS_TOKEN từ CaiDat, gọi /me/accounts và ghi vào sheet 'Quanlypage'
 * Cột: Tên Page | Page ID | Ngày hoạt động (thời gian chạy)
 */
function lietKeFanpageQuanLy() {
  var settings = getSettingsSafe_();
  var accessToken = settings['ACCESS_TOKEN'];
  var botToken = settings['TELEGRAM_BOT_TOKEN'];
  var chatId = settings['TELEGRAM_CHAT_ID'];
  if (!accessToken) {
    if (botToken && chatId) guiThongBaoTelegram('⚠️ Thiếu ACCESS_TOKEN trong CaiDat. Không thể liệt kê Page.', botToken, chatId);
    return;
  }

  var ss = getSpreadsheet_();
  var sh = ss.getSheetByName('Quanlypage') || ss.insertSheet('Quanlypage');
  sh.clearContents();
  sh.getRange(1, 1, 1, 3).setValues([[ 'Tên Page', 'Page ID', 'Ngày hoạt động' ]]);

  var pages = [];
  try {
    pages = pages.concat(fetchPagesFromMeAccounts_(accessToken));
  } catch (e) {
    Logger.log("⚠️ Lỗi fetchPagesFromMeAccounts_: " + e.message);
  }

  // Fallback qua Business nếu /me/accounts rỗng (System User, BM quản lý)
  if (pages.length === 0) {
    try { 
      pages = pages.concat(fetchPagesFromBusinesses_(accessToken)); 
    } catch (e2) {
      Logger.log("⚠️ Lỗi fetchPagesFromBusinesses_: " + e2.message);
    }
  }

  if (pages.length > 0) {
    // TỐI ƯU: Unique by Page ID - dùng object thay vì forEach
    var seen = {};
    var uniq = [];
    var now = new Date();
    for (var i = 0; i < pages.length; i++) {
      var id = pages[i][1];
      if (id && !seen[id]) {
        seen[id] = true;
        uniq.push(pages[i]);
      }
    }
    
    if (uniq.length > 0) {
      sh.getRange(2, 1, uniq.length, 3).setValues(uniq);
      if (botToken && chatId) {
        try {
          guiThongBaoTelegram('✅ Đã liệt kê ' + uniq.length + ' Page vào Quanlypage.', botToken, chatId);
        } catch(_n) {}
      }
    }
  } else {
    if (botToken && chatId) {
      guiThongBaoTelegram('ℹ️ Không tìm thấy Page nào. Vui lòng kiểm tra lại token (pages_show_list) hoặc quyền trong Business Manager.', botToken, chatId);
    }
  }
}

function fetchPagesFromMeAccounts_(accessToken) {
  var out = [];
  var url = 'https://graph.facebook.com/v24.0/me/accounts' +
            '?fields=id,name,access_type,perms,tasks' +
            '&limit=100' +
            '&access_token=' + encodeURIComponent(accessToken);
  
  // TỐI ƯU: Cache manageTasks array
  var manageTasks = ['MANAGE','ADVERTISE','MODERATE','CREATE_CONTENT','ANALYZE'];
  var manageTasksSet = {};
  for (var mt = 0; mt < manageTasks.length; mt++) {
    manageTasksSet[manageTasks[mt]] = true;
  }
  
  var now = new Date();
  while (url) {
    var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var json = JSON.parse(resp.getContentText());
    if (json.error) throw new Error(json.error.message + ' (code ' + json.error.code + ')');
    var data = Array.isArray(json.data) ? json.data : [];
    
    // TỐI ƯU: Dùng for thay vì forEach
    for (var i = 0; i < data.length; i++) {
      var p = data[i];
      var perms = p.perms || [];
      var tasks = p.tasks || [];
      var accessType = p.access_type || '';
      
      // TỐI ƯU: Dùng object lookup thay vì indexOf
      var hasAdminPerm = false;
      for (var j = 0; j < perms.length; j++) {
        if (perms[j] === 'ADMINISTER') {
          hasAdminPerm = true;
          break;
        }
      }
      
      // TỐI ƯU: Dùng object lookup thay vì some + indexOf
      var hasManageTask = false;
      for (var k = 0; k < tasks.length; k++) {
        var taskUpper = String(tasks[k]).toUpperCase();
        if (manageTasksSet[taskUpper]) {
          hasManageTask = true;
          break;
        }
      }
      
      var isOwner = String(accessType).toUpperCase() === 'OWNER';
      if (hasAdminPerm || hasManageTask || isOwner || (perms.length === 0 && tasks.length === 0)) {
        out.push([ p.name || '', p.id || '', now ]);
      }
    }
    url = (json.paging && json.paging.next) ? json.paging.next : '';
  }
  return out;
}

function fetchPagesFromBusinesses_(accessToken) {
  var out = [];
  // Lấy danh sách Business mà token có quyền
  var urlBiz = 'https://graph.facebook.com/v24.0/me/businesses?limit=100&access_token=' + encodeURIComponent(accessToken);
  var bizIds = [];
  
  // TỐI ƯU: Dùng for thay vì while + forEach
  while (urlBiz) {
    var r = UrlFetchApp.fetch(urlBiz, { muteHttpExceptions: true });
    var j = JSON.parse(r.getContentText());
    if (j.error) throw new Error(j.error.message + ' (code ' + j.error.code + ')');
    var d = Array.isArray(j.data) ? j.data : [];
    
    for (var i = 0; i < d.length; i++) {
      if (d[i] && d[i].id) bizIds.push(d[i].id);
    }
    urlBiz = (j.paging && j.paging.next) ? j.paging.next : '';
  }
  
  // TỐI ƯU: Cache edges và now
  var edges = ['owned_pages','client_pages'];
  var now = new Date();
  
  // Với mỗi business, lấy owned_pages và client_pages
  for (var bidIdx = 0; bidIdx < bizIds.length; bidIdx++) {
    var bid = bizIds[bidIdx];
    for (var edgeIdx = 0; edgeIdx < edges.length; edgeIdx++) {
      var edge = edges[edgeIdx];
      var url = 'https://graph.facebook.com/v24.0/' + bid + '/' + edge + '?fields=id,name&limit=100&access_token=' + encodeURIComponent(accessToken);
      while (url) {
        var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
        var json = JSON.parse(resp.getContentText());
        if (json.error) break;
        var data = Array.isArray(json.data) ? json.data : [];
        
        // TỐI ƯU: Dùng for thay vì forEach
        for (var pIdx = 0; pIdx < data.length; pIdx++) {
          var p = data[pIdx];
          out.push([ p.name || '', p.id || '', now ]);
        }
        url = (json.paging && json.paging.next) ? json.paging.next : '';
      }
    }
  }
  return out;
}

/**
 * Lấy các bài viết gần nhất từ một Page cụ thể
 * @param {string} pageId - ID của Page (ví dụ: "502595182941251")
 * @param {number} limit - Số bài viết muốn lấy (mặc định: 25)
 */
function layBaiVietGanNhat(pageId, limit) {
  var settings = getSettingsSafe_();
  var accessToken = settings['ACCESS_TOKEN'];
  var botToken = settings['TELEGRAM_BOT_TOKEN'];
  var chatId = settings['TELEGRAM_CHAT_ID'];
  
  if (!accessToken) {
    if (botToken && chatId) guiThongBaoTelegram('⚠️ Thiếu ACCESS_TOKEN trong CaiDat.', botToken, chatId);
    return;
  }
  
  if (!pageId) {
    if (botToken && chatId) guiThongBaoTelegram('⚠️ Chưa cung cấp Page ID.', botToken, chatId);
    return;
  }
  
  limit = limit || 25;
  
  var ss = getSpreadsheet_();
  var sh = ss.getSheetByName('Posts_Page') || ss.insertSheet('Posts_Page');
  sh.clearContents();
  sh.getRange(1, 1, 1, 5).setValues([[ 'Post ID', 'Nội dung', 'Link bài viết', 'Ngày đăng', 'Page ID' ]]);
  
  var posts = [];
  var url = 'https://graph.facebook.com/v24.0/' + pageId + '/published_posts' +
            '?fields=id,message,permalink_url,created_time' +
            '&limit=' + limit +
            '&access_token=' + encodeURIComponent(accessToken);
  
  try {
    var resp = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var json = JSON.parse(resp.getContentText());
    
    if (json.error) {
      throw new Error(json.error.message + ' (code ' + json.error.code + ')');
    }
    
    var data = Array.isArray(json.data) ? json.data : [];
    
    // TỐI ƯU: Dùng for thay vì forEach
    for (var i = 0; i < data.length; i++) {
      var post = data[i];
      var permalink = post.permalink_url || '';
      if (!permalink && post.id) {
        permalink = 'https://www.facebook.com/' + post.id;
      }
      posts.push([
        post.id || '',
        post.message || '(Không có nội dung)',
        permalink,
        post.created_time || '',
        pageId
      ]);
    }
    
    if (posts.length > 0) {
      sh.getRange(2, 1, posts.length, 5).setValues(posts);
      if (botToken && chatId) {
        guiThongBaoTelegram('✅ Đã lấy ' + posts.length + ' bài viết gần nhất từ Page ID: ' + pageId, botToken, chatId);
      }
    } else {
      if (botToken && chatId) {
        guiThongBaoTelegram('ℹ️ Không tìm thấy bài viết nào từ Page ID: ' + pageId, botToken, chatId);
      }
    }
  } catch (e) {
    Logger.log("🚨 Lỗi khi lấy bài viết: " + e.message);
    if (botToken && chatId) {
      guiThongBaoTelegram('🚨 Lỗi khi lấy bài viết: ' + e.message, botToken, chatId);
    }
  }
}

/**
 * Lấy bài viết từ Page MCS STORE (ID: 502595182941251)
 */
function layBaiVietMCSStore() {
  layBaiVietGanNhat('502595182941251', 25);
}
