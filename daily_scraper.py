<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新能源重卡市場情報與 TCO 中樞 (EV-Truck-Hub)</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased">

    <!-- 頂部導航欄 -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
                <h1 class="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                    ⚡ 新能源純電重卡情報與 TCO 中樞
                </h1>
                <p class="text-xs text-slate-400 mt-1">雙引擎 AI 智慧聚合架構 ｜ 內建 TCO 算帳神器、政策路權與供應鏈</p>
            </div>
            <div class="flex items-center gap-3">
                <!-- 🧮 算帳神器按鈕 -->
                <button onclick="openTcoModal()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition shadow-lg shadow-emerald-900/30 flex items-center gap-2">
                    🧮 開啟 TCO 算帳神器
                </button>
                <button onclick="shuffleNews()" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition shadow-lg shadow-blue-900/30 flex items-center gap-2">
                    🔄 換一批探索
                </button>
                <span id="update-time" class="text-xs bg-slate-800 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700"></span>
            </div>
        </div>
    </header>

    <!-- 主要佈局 -->
    <main class="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- 左側與中間：即時情報流 (佔 2 欄) -->
        <section class="lg:col-span-2 space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-lg font-semibold text-slate-200 flex items-center gap-2">
                    📡 <span>今日智慧早報與 TCO 情報流</span>
                    <span id="news-count" class="text-xs bg-blue-950 text-blue-400 border border-blue-800 px-2 py-0.5 rounded-full">0 條</span>
                </h2>
                <span class="text-xs text-slate-400">點擊卡片按鈕收納或記錄</span>
            </div>

            <!-- 情報卡片掛載容器 -->
            <div id="news-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- 動態載入 -->
            </div>
        </section>

        <!-- 右側：互動專區 (自選欄目 & 3天歷史足跡資料夾) -->
        <aside class="space-y-6">
            
            <!-- 自選欄目 (我的收藏) -->
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-semibold text-emerald-400 flex items-center gap-2">
                        📌 <span>我的自選欄目</span>
                        <span id="custom-count" class="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">0</span>
                    </h3>
                    <button onclick="clearCustom()" class="text-xs text-slate-500 hover:text-red-400 transition">清空</button>
                </div>
                <div id="custom-container" class="space-y-3 max-h-96 overflow-y-auto pr-1">
                    <p class="text-xs text-slate-500 text-center py-6">尚未添加任何情報，請從左側點擊「加入自選欄目」</p>
                </div>
            </div>

            <!-- 3 天歷史足跡 (資料夾折疊入口) -->
            <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
                <button onclick="toggleHistoryFolder()" class="w-full p-4 flex justify-between items-center bg-slate-900 hover:bg-slate-850 transition">
                    <div class="flex items-center gap-2">
                        <span id="folder-icon" class="text-amber-400">📁</span>
                        <span class="font-semibold text-slate-200 text-sm">3天歷史足跡紀錄</span>
                        <span id="history-count" class="text-[10px] bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded-full">0</span>
                    </div>
                    <span id="folder-arrow" class="text-xs text-slate-400 transition transform">▼ 展開</span>
                </button>
                <div id="history-drawer" class="hidden border-t border-slate-800 p-4 space-y-2.5 max-h-60 overflow-y-auto bg-slate-950/50">
                    <div id="history-container" class="space-y-2">
                        <p class="text-xs text-slate-500 text-center py-4">尚無歷史足跡紀錄</p>
                    </div>
                </div>
            </div>

        </aside>
    </main>

    <!-- 🧮 TCO 算帳神器彈出視窗 (Modal) -->
    <div id="tco-modal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl p-6 shadow-2xl space-y-6">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                <h3 class="text-lg font-bold text-emerald-400 flex items-center gap-2">
                    🧮 新能源純電重卡 TCO 精算神器
                </h3>
                <button onclick="closeTcoModal()" class="text-slate-400 hover:text-slate-200 text-lg">✕</button>
            </div>

            <!-- 輸入參數區 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                    <label class="block text-xs text-slate-400 mb-1">年行駛里程 (公里)</label>
                    <input type="number" id="tco-km" value="150000" oninput="calculateTco()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="block text-xs text-slate-400 mb-1">柴油車油耗 (升/100公里)</label>
                    <input type="number" id="tco-diesel-rate" value="38" oninput="calculateTco()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="block text-xs text-slate-400 mb-1">柴油單價 (元/升)</label>
                    <input type="number" id="tco-diesel-price" value="7.5" oninput="calculateTco()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="block text-xs text-slate-400 mb-1">純電重卡電耗 (度/100公里)</label>
                    <input type="number" id="tco-ev-rate" value="130" oninput="calculateTco()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="block text-xs text-slate-400 mb-1">綜合電費單價 (元/度)</label>
                    <input type="number" id="tco-electric-price" value="0.75" oninput="calculateTco()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
                <div>
                    <label class="block text-xs text-slate-400 mb-1">車價差額 (純電高出柴油車)</label>
                    <input type="number" id="tco-price-diff" value="150000" oninput="calculateTco()" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500">
                </div>
            </div>

            <!-- 計算結果展示區 -->
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 grid grid-cols-3 gap-4 text-center">
                <div>
                    <span class="text-xs text-slate-400 block mb-1">柴油車年燃料費</span>
                    <span id="res-diesel-cost" class="text-base font-bold text-red-400">0 元</span>
                </div>
                <div>
                    <span class="text-xs text-slate-400 block mb-1">純電重卡年電費</span>
                    <span id="res-ev-cost" class="text-base font-bold text-blue-400">0 元</span>
                </div>
                <div>
                    <span class="text-xs text-slate-400 block mb-1">年省金額 (TCO 效益)</span>
                    <span id="res-saving" class="text-base font-bold text-emerald-400">0 元</span>
                </div>
            </div>

            <!-- 回本週期提示 -->
            <div id="res-payback" class="text-center p-3 bg-emerald-950/40 border border-emerald-900/60 rounded-xl text-xs text-emerald-300 font-medium">
                <!-- 動態計算 -->
            </div>

            <div class="flex justify-end">
                <button onclick="closeTcoModal()" class="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm transition">關閉算帳神器</button>
            </div>
        </div>
    </div>

    <!-- 前端互動邏輯 -->
    <script>
        let allNewsData = [];
        let customItems = JSON.parse(localStorage.getItem('ev_custom_items') || '[]');

        window.addEventListener('DOMContentLoaded', () => {
            loadNews();
            renderCustomItems();
            cleanAndRenderHistory();
            calculateTco();
        });

        // 載入數據與備用多維度擴充
        async function loadNews() {
            try {
                const response = await fetch('today_news.json?t=' + Date.now());
                if (!response.ok) throw new Error('無法載入');
                let data = await response.json();
                
                if (data.length < 5) {
                    const richFallback = [
                        { category: "policy", tag: "🏛️ 政策路权", title: "多地交通厅发文扩大重卡通行路权", date: "2026-11-09", summary: "北方多省市近期针对纯电动牵引车出台市区通行证优先办理政策，大幅降低干线物流最后一公里成本。", action: "建议销售团队立即向市区周边大型物流园区客户推送路权红利政策。" },
                        { category: "tco", tag: "📊 TCO 经济性", title: "400kWh 换电重卡全生命周期回本周期测算", date: "2026-11-09", summary: "随着电池电芯成本回落，配合换电站 5 分钟补能模式，年行驶 15 万公里的纯电重卡 TCO 较柴油车节省达 35%。", action: "立即更新最新 TCO 试算表，针对高频干线物流车队主打 2.5 年回本优势。" },
                        { category: "battery", tag: "🔋 电池与补能", title: "重卡超充與重载换电技术路线对比", date: "2026-11-09", summary: "头部电池厂发布新一代重卡专用长寿命电池，支持 2C 快充，有效解決高寒地區冬季續航衰減痛點。", action: "向北方礦山與重載短倒客戶推介耐寒熱管理系統優勢。" },
                        { category: "competitor", tag: "🎯 竞品动态", title: "三一重工发布新一代大电量换电重卡", date: "2026-11-09", summary: "竞品推出针对重载矿山场景的 600kWh 超大电量换电车型，主打全天候高强度连续施工作业。", action: "针对标案客戶，需強調我方車型在三电系统熱管理與自重上的對比優勢。" },
                        { category: "supply", tag: "🌐 供应链与出海", title: "国内新能源重卡加速开拓中亚與东南亚市场", date: "2026-11-09", summary: "受国内换电基础设施成熟带动，多家主机厂成功向中亚矿业集团交付百辆级纯电自卸车。", action: "評估跨境物流大宗物資運輸企業的海外換電站配套需求。" }
                    ];
                    const titles = new Set(data.map(i => i.title));
                    richFallback.forEach(item => {
                        if (!titles.has(item.title)) data.push(item);
                    });
                }

                allNewsData = data;
                document.getElementById('update-time').innerText = `更新於: ${new Date().toLocaleDateString()}`;
                renderNews(allNewsData);
            } catch (error) {
                console.error(error);
                allNewsData = [
                    { category: "tco", tag: "📊 TCO 经济性", title: "重卡營運 TCO 試算模型優化", date: "2026-11-09", summary: "油气价差缩窄背景下，纯电重卡在固定线路短倒中展现出极致的度电成本优势。", action: "向客户提供客製化 TCO 對比報告。" }
                ];
                renderNews(allNewsData);
            }
        }

        function renderNews(data) {
            const container = document.getElementById('news-container');
            document.getElementById('news-count').innerText = `${data.length} 條`;
            
            container.innerHTML = data.map((item, index) => `
                <div class="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 flex flex-col justify-between transition shadow-md">
                    <div>
                        <div class="flex justify-between items-start gap-2 mb-3">
                            <span class="text-xs px-2.5 py-1 bg-slate-800 text-blue-300 font-medium rounded-md border border-slate-700">${item.tag || '💡 行業動態'}</span>
                            <span class="text-xs text-slate-500">${item.date || ''}</span>
                        </div>
                        <h3 class="font-semibold text-slate-100 text-base mb-2">${item.title}</h3>
                        <p class="text-slate-400 text-xs leading-relaxed mb-4">${item.summary}</p>
                        <div class="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 mb-4">
                            <span class="text-xs font-semibold text-emerald-400 block mb-1">💡 實戰應對建議：</span>
                            <p class="text-xs text-slate-300">${item.action}</p>
                        </div>
                    </div>
                    <div class="flex gap-2 pt-2 border-t border-slate-800/60">
                        <button onclick='addToCustom(${JSON.stringify(item).replace(/'/g, "&apos;")})' class="flex-1 py-2 bg-slate-800 hover:bg-emerald-600 hover:text-white text-xs font-medium text-slate-300 rounded-lg transition text-center">
                            📌 加入自選欄目
                        </button>
                        <button onclick='recordHistory(${JSON.stringify(item).replace(/'/g, "&apos;")})' class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-xs text-slate-400 rounded-lg transition" title="記錄瀏覽">
                            👁️ 記錄
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // 換一批探索
        function shuffleNews() {
            if (allNewsData.length === 0) return;
            const shuffled = [...allNewsData].sort(() => 0.5 - Math.random());
            renderNews(shuffled);
        }

        // 自選欄目邏輯
        function addToCustom(item) {
            if (!customItems.some(i => i.title === item.title)) {
                customItems.push(item);
                localStorage.setItem('ev_custom_items', JSON.stringify(customItems));
                renderCustomItems();
            }
        }

        function renderCustomItems() {
            const container = document.getElementById('custom-container');
            document.getElementById('custom-count').innerText = customItems.length;

            if (customItems.length === 0) {
                container.innerHTML = `<p class="text-xs text-slate-500 text-center py-6">尚未添加任何情報，請從左側點擊「加入自選欄目」</p>`;
                return;
            }

            container.innerHTML = customItems.map((item, index) => `
                <div class="p-3 bg-slate-950 border border-slate-800 rounded-lg flex justify-between items-start gap-2">
                    <div>
                        <span class="text-[10px] text-emerald-400 font-medium">${item.tag}</span>
                        <h4 class="text-xs font-medium text-slate-200 mt-0.5 line-clamp-1">${item.title}</h4>
                    </div>
                    <button onclick="removeFromCustom(${index})" class="text-slate-500 hover:text-red-400 text-xs px-1">✕</button>
                </div>
            `).join('');
        }

        function removeFromCustom(index) {
            customItems.splice(index, 1);
            localStorage.setItem('ev_custom_items', JSON.stringify(customItems));
            renderCustomItems();
        }

        function clearCustom() {
            customItems = [];
            localStorage.removeItem('ev_custom_items');
            renderCustomItems();
        }

        // 3 天歷史足跡資料夾折疊開關邏輯
        function toggleHistoryFolder() {
            const drawer = document.getElementById('history-drawer');
            const arrow = document.getElementById('folder-arrow');
            const icon = document.getElementById('folder-icon');
            
            if (drawer.classList.contains('hidden')) {
                drawer.classList.remove('hidden');
                arrow.innerText = '▲ 收合';
                icon.innerText = '📂';
            } else {
                drawer.classList.add('hidden');
                arrow.innerText = '▼ 展開';
                icon.innerText = '📁';
            }
        }

        // 歷史足跡紀錄 (保留 3 天)
        function recordHistory(item) {
            let history = JSON.parse(localStorage.getItem('ev_news_history') || '[]');
            const now = Date.now();

            history = history.filter(h => h.title !== item.title);
            history.unshift({ ...item, timestamp: now });

            const THREE_DAYS = 3 * 24 * 60 * 60 * 1000;
            history = history.filter(h => (now - h.timestamp) < THREE_DAYS);

            localStorage.setItem('ev_news_history', JSON.stringify(history));
            cleanAndRenderHistory();
        }

        function cleanAndRenderHistory() {
            const container = document.getElementById('history-container');
            let history = JSON.parse(localStorage.getItem('ev_news_history') || '[]');
            const now = Date.now();
            const THREE_DAYS = 3 * 24 * 60 * 60 * 1000;

            history = history.filter(h => (now - h.timestamp) < THREE_DAYS);
            localStorage.setItem('ev_news_history', JSON.stringify(history));
            document.getElementById('history-count').innerText = history.length;

            if (history.length === 0) {
                container.innerHTML = `<p class="text-xs text-slate-500 text-center py-4">尚無歷史足跡紀錄</p>`;
                return;
            }

            container.innerHTML = history.map(h => {
                const timeDiffHours = Math.floor((now - h.timestamp) / (1000 * 60 * 60));
                const timeStr = timeDiffHours < 24 ? `${timeDiffHours} 小時前` : `${Math.floor(timeDiffHours / 24)} 天前`;
                return `
                    <div class="p-2.5 bg-slate-900 border border-slate-800 rounded-lg">
                        <div class="flex justify-between items-center text-[10px] text-slate-500 mb-1">
                            <span>${h.tag}</span>
                            <span>${timeStr}</span>
                        </div>
                        <p class="text-xs text-slate-300 line-clamp-1">${h.title}</p>
                    </div>
                `;
            }).join('');
        }

        // 🧮 TCO 算帳神器彈窗邏輯與計算引擎
        function openTcoModal() {
            document.getElementById('tco-modal').classList.remove('hidden');
        }

        function closeTcoModal() {
            document.getElementById('tco-modal').classList.add('hidden');
        }

        function calculateTco() {
            const km = parseFloat(document.getElementById('tco-km').value) || 0;
            const dieselRate = parseFloat(document.getElementById('tco-diesel-rate').value) || 0;
            const dieselPrice = parseFloat(document.getElementById('tco-diesel-price').value) || 0;
            const evRate = parseFloat(document.getElementById('tco-ev-rate').value) || 0;
            const electricPrice = parseFloat(document.getElementById('tco-electric-price').value) || 0;
            const priceDiff = parseFloat(document.getElementById('tco-price-diff').value) || 0;

            const dieselCost = (km / 100) * dieselRate * dieselPrice;
            const evCost = (km / 100) * evRate * electricPrice;
            const annualSaving = dieselCost - evCost;

            document.getElementById('res-diesel-cost').innerText = dieselCost.toLocaleString('zh-CN', { maximumFractionDigits: 0 }) + ' 元';
            document.getElementById('res-ev-cost').innerText = evCost.toLocaleString('zh-CN', { maximumFractionDigits: 0 }) + ' 元';
            document.getElementById('res-saving').innerText = annualSaving.toLocaleString('zh-CN', { maximumFractionDigits: 0 }) + ' 元';

            const paybackDiv = document.getElementById('res-payback');
            if (annualSaving > 0) {
                const paybackYears = priceDiff / annualSaving;
                const paybackMonths = (paybackYears * 12).toFixed(1);
                paybackDiv.innerHTML = `💡 實戰結論：車價差額可在 <span class="text-emerald-300 font-bold underline text-sm">${paybackMonths} 個月</span>（約 ${(paybackYears).toFixed(1)} 年）內透過燃料差價完全回本！`;
            } else {
                paybackDiv.innerHTML = `⚠️ 目前參數設定下純電成本高於柴油，請調整油電單價或耗能參數。`;
            }
        }
    </script>
</body>
</html>
