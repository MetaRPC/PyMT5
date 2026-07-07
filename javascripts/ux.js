// PyMT5 — Enhanced UX
document.addEventListener('DOMContentLoaded', function() {
  console.log('PyMT5 Documentation loaded');

  // Initialize Progress Tracker
  initProgressTracker();

  // Initialize Contact Panel
  initContactPanel();
});

// ============================================================================
// PROGRESS TRACKER - Track documentation reading progress
// ============================================================================

const PROGRESS_STORAGE_KEY = 'pymt5_docs_progress';

// Documentation structure for PyMT5 - ALL pages tracked
const DOC_STRUCTURE = {
  'guides': {
    name: '📘 Guides',
    pages: [
      'All_Guides/GETTING_STARTED',
      'All_Guides/Your_First_Project',
      'All_Guides/PROJECT_MAP',
      'All_Guides/GLOSSARY',
      'All_Guides/MT5_For_Beginners',
      'All_Guides/GRPC_STREAM_MANAGEMENT',
      'All_Guides/RETURN_CODES_REFERENCE',
      'All_Guides/PROTOBUF_INSPECTOR_GUIDE',
      'All_Guides/USERCODE_SANDBOX_GUIDE',
      'All_Guides/ENUMS_USAGE_REFERENCE'
    ]
  },
  'mt5account': {
    name: '📦 MT5Account',
    pages: [
      'MT5Account/MT5Account.Master.Overview',
      'MT5Account/1. Account_Information/Account_Information.Overview',
      'MT5Account/1. Account_Information/account_info_double',
      'MT5Account/1. Account_Information/account_info_integer',
      'MT5Account/1. Account_Information/account_info_string',
      'MT5Account/1. Account_Information/account_summary',
      'MT5Account/2. Symbol_Information/Symbol_Information.Overview',
      'MT5Account/2. Symbol_Information/symbol_exist',
      'MT5Account/2. Symbol_Information/symbol_info_double',
      'MT5Account/2. Symbol_Information/symbol_info_integer',
      'MT5Account/2. Symbol_Information/symbol_info_margin_rate',
      'MT5Account/2. Symbol_Information/symbol_info_session_quote',
      'MT5Account/2. Symbol_Information/symbol_info_session_trade',
      'MT5Account/2. Symbol_Information/symbol_info_string',
      'MT5Account/2. Symbol_Information/symbol_info_tick',
      'MT5Account/2. Symbol_Information/symbol_is_synchronized',
      'MT5Account/2. Symbol_Information/symbol_name',
      'MT5Account/2. Symbol_Information/symbol_params_many',
      'MT5Account/2. Symbol_Information/symbol_select',
      'MT5Account/2. Symbol_Information/symbols_total',
      'MT5Account/3. Positions_Orders/Positions_Orders.Overview',
      'MT5Account/3. Positions_Orders/opened_orders',
      'MT5Account/3. Positions_Orders/opened_orders_tickets',
      'MT5Account/3. Positions_Orders/order_history',
      'MT5Account/3. Positions_Orders/positions_history',
      'MT5Account/3. Positions_Orders/positions_total',
      'MT5Account/3. Positions_Orders/tick_value_with_size',
      'MT5Account/4. Market_Depth/Market_Depth.Overview',
      'MT5Account/4. Market_Depth/market_book_add',
      'MT5Account/4. Market_Depth/market_book_get',
      'MT5Account/4. Market_Depth/market_book_release',
      'MT5Account/5. Trading_Operations/Trading_Operations.Overview',
      'MT5Account/5. Trading_Operations/order_calc_margin',
      'MT5Account/5. Trading_Operations/order_calc_profit',
      'MT5Account/5. Trading_Operations/order_check',
      'MT5Account/5. Trading_Operations/order_close',
      'MT5Account/5. Trading_Operations/order_modify',
      'MT5Account/5. Trading_Operations/order_send',
      'MT5Account/6. Streaming_Methods/Streaming_Methods.Overview',
      'MT5Account/6. Streaming_Methods/on_position_profit',
      'MT5Account/6. Streaming_Methods/on_positions_and_pending_orders_tickets',
      'MT5Account/6. Streaming_Methods/on_symbol_tick',
      'MT5Account/6. Streaming_Methods/on_trade',
      'MT5Account/6. Streaming_Methods/on_trade_transaction',
      'MT5Account/HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW',
      'MT5Account/HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW',
      'MT5Account/HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW',
      'MT5Account/HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW',
      'MT5Account/HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW',
      'MT5Account/HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW',
      'MT5Account/HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_tickets_HOW',
      'MT5Account/HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW',
      'MT5Account/HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW',
      'MT5Account/HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_total_HOW',
      'MT5Account/HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW',
      'MT5Account/HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW',
      'MT5Account/HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW',
      'MT5Account/HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW',
      'MT5Account/HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW',
      'MT5Account/HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW',
      'MT5Account/HOW_IT_WORK/5. Trading_Operations_HOW/order_check_HOW',
      'MT5Account/HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW',
      'MT5Account/HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW',
      'MT5Account/HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW',
      'MT5Account/HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW',
      'MT5Account/HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW',
      'MT5Account/HOW_IT_WORK/6. Streaming_Methods_HOW/on_symbol_tick_HOW',
      'MT5Account/HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW',
      'MT5Account/HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW'
    ]
  },
  'mt5service': {
    name: '🔧 MT5Service',
    pages: [
      'MT5Service/MT5Service.Overview',
      'MT5Service/1. Account_Information',
      'MT5Service/2. Symbol_Information',
      'MT5Service/3. Positions_Orders',
      'MT5Service/4. Market_Depth',
      'MT5Service/5. Trading_Operations',
      'MT5Service/6. Streaming_Methods'
    ]
  },
  'mt5sugar': {
    name: '🍬 MT5Sugar',
    pages: [
      'MT5Sugar/MT5Sugar.Master.Overview',
      'MT5Sugar/1. Connection/is_connected',
      'MT5Sugar/1. Connection/ping',
      'MT5Sugar/1. Connection/quick_connect',
      'MT5Sugar/2. Account_Properties/balance_property',
      'MT5Sugar/2. Account_Properties/get_account_info',
      'MT5Sugar/2. Account_Properties/get_balance',
      'MT5Sugar/2. Account_Properties/get_equity',
      'MT5Sugar/2. Account_Properties/get_floating_profit',
      'MT5Sugar/2. Account_Properties/get_free_margin',
      'MT5Sugar/2. Account_Properties/get_margin',
      'MT5Sugar/2. Account_Properties/get_margin_level',
      'MT5Sugar/3. Prices_Quotes/get_ask',
      'MT5Sugar/3. Prices_Quotes/get_bid',
      'MT5Sugar/3. Prices_Quotes/get_price_info',
      'MT5Sugar/3. Prices_Quotes/get_spread',
      'MT5Sugar/3. Prices_Quotes/wait_for_price',
      'MT5Sugar/4. Simple_Trading/buy_limit',
      'MT5Sugar/4. Simple_Trading/buy_market',
      'MT5Sugar/4. Simple_Trading/buy_stop',
      'MT5Sugar/4. Simple_Trading/sell_limit',
      'MT5Sugar/4. Simple_Trading/sell_market',
      'MT5Sugar/4. Simple_Trading/sell_stop',
      'MT5Sugar/5. Trading_With_SLTP/buy_limit_with_sltp',
      'MT5Sugar/5. Trading_With_SLTP/buy_market_with_sltp',
      'MT5Sugar/5. Trading_With_SLTP/sell_limit_with_sltp',
      'MT5Sugar/5. Trading_With_SLTP/sell_market_with_sltp',
      'MT5Sugar/6. Position_Management/close_all_positions',
      'MT5Sugar/6. Position_Management/close_position',
      'MT5Sugar/6. Position_Management/close_position_partial',
      'MT5Sugar/6. Position_Management/modify_position_sl',
      'MT5Sugar/6. Position_Management/modify_position_sltp',
      'MT5Sugar/6. Position_Management/modify_position_tp',
      'MT5Sugar/7. Position_Information/count_open_positions',
      'MT5Sugar/7. Position_Information/get_open_positions',
      'MT5Sugar/7. Position_Information/get_position_by_ticket',
      'MT5Sugar/7. Position_Information/get_positions_by_symbol',
      'MT5Sugar/7. Position_Information/get_profit_by_symbol',
      'MT5Sugar/7. Position_Information/get_total_profit',
      'MT5Sugar/7. Position_Information/has_open_position',
      'MT5Sugar/8. History_Statistics/get_daily_stats',
      'MT5Sugar/8. History_Statistics/get_deals',
      'MT5Sugar/8. History_Statistics/get_profit',
      'MT5Sugar/9. Symbol_Information/get_all_symbols',
      'MT5Sugar/9. Symbol_Information/get_min_stop_level',
      'MT5Sugar/9. Symbol_Information/get_symbol_digits',
      'MT5Sugar/9. Symbol_Information/get_symbol_info',
      'MT5Sugar/9. Symbol_Information/is_symbol_available',
      'MT5Sugar/10. Risk_Management/calculate_position_size',
      'MT5Sugar/10. Risk_Management/calculate_required_margin',
      'MT5Sugar/10. Risk_Management/can_open_position',
      'MT5Sugar/10. Risk_Management/get_max_lot_size'
    ]
  },
  'api_reference': {
    name: '📚 API Reference',
    pages: [
      'API_Reference/MT5Account',
      'API_Reference/MT5Service',
      'API_Reference/MT5Sugar'
    ]
  }
};

function initProgressTracker() {
  // Track current page visit
  trackPageVisit();

  // Create and inject progress bar
  createProgressBar();

  // Update progress display
  updateProgressDisplay();

  // Track link clicks for navigation
  trackLinkClicks();

  // Track browser back/forward navigation
  window.addEventListener('popstate', function() {
    setTimeout(() => {
      trackPageVisit();
      updateProgressDisplay();
    }, 100);
  });

  // Track dynamic content changes (for Material for MkDocs instant loading)
  if (window.MutationObserver) {
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.target.classList.contains('md-content')) {
          setTimeout(() => {
            trackPageVisit();
            updateProgressDisplay();
          }, 100);
        }
      });
    });

    const contentElement = document.querySelector('.md-content');
    if (contentElement) {
      observer.observe(contentElement, { childList: true, subtree: true });
    }
  }
}

function trackLinkClicks() {
  // Track all internal documentation links
  document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href]');
    if (!link) return;

    const href = link.getAttribute('href');

    // Skip external links, anchors, and non-doc links
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto:')) {
      return;
    }

    // Wait a bit for navigation to complete, then track
    setTimeout(() => {
      const oldProgress = getProgress();
      const oldCount = oldProgress.visitedPages.length;

      trackPageVisit();

      const newProgress = getProgress();
      const newCount = newProgress.visitedPages.length;

      // Only update display if progress actually changed
      if (newCount > oldCount) {
        updateProgressDisplay();
      }
    }, 200);
  }, true);
}

function trackPageVisit() {
  const currentPath = getCurrentPagePath();
  if (!currentPath) return;

  const progress = getProgress();
  if (!progress.visitedPages.includes(currentPath)) {
    progress.visitedPages.push(currentPath);
    progress.lastVisit = new Date().toISOString();
    saveProgress(progress);
  }
}

function getCurrentPagePath() {
  // Get current page path from URL
  let path = window.location.pathname;

  // Remove .html extension if present
  path = path.replace(/\.html$/, '');

  // Try multiple patterns to extract the page path
  // Pattern 1: GitHub Pages - /PyMT5/path/to/page/
  let match = path.match(/\/PyMT5\/(.+?)(?:\/)?$/);
  if (match && match[1] !== '') {
    // Decode URL encoding (e.g., %20 -> space)
    return decodeURIComponent(match[1].replace(/\/$/, ''));
  }

  // Pattern 2: Local server - /path/to/page/
  match = path.match(/^\/(.+?)(?:\/)?$/);
  if (match && match[1] !== '' && match[1] !== 'index') {
    // Decode URL encoding (e.g., %20 -> space)
    return decodeURIComponent(match[1].replace(/\/$/, ''));
  }

  // Pattern 3: Index page
  if (path === '/' || path === '/PyMT5/' || path === '/index' || path === '/PyMT5/index') {
    return 'index';
  }

  console.log('Could not extract page path from:', path);
  return null;
}

function getProgress() {
  const stored = localStorage.getItem(PROGRESS_STORAGE_KEY);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (e) {
      console.error('Failed to parse progress data:', e);
    }
  }

  // Default progress structure
  return {
    visitedPages: [],
    lastVisit: new Date().toISOString()
  };
}

function saveProgress(progress) {
  localStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(progress));
}

function createProgressBar() {
  // Check if progress bar already exists
  if (document.getElementById('progress-float-btn')) return;

  const progressHTML = `
    <!-- Mini Header Progress Bar -->
    <div class="header-progress-bar">
      <div class="header-progress-fill" id="header-progress-fill" style="width: 0%"></div>
    </div>

    <!-- Floating Button with Circular Progress -->
    <button id="progress-float-btn" class="progress-float-btn" title="Learning Progress">
      <!-- Circular Progress SVG -->
      <svg class="progress-ring" width="66" height="66">
        <defs>
          <linearGradient id="progress-gradient-light" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#0078D4"/>
            <stop offset="100%" stop-color="#00D9C0"/>
          </linearGradient>
          <linearGradient id="progress-gradient-dark" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00D9C0"/>
            <stop offset="100%" stop-color="#0078D4"/>
          </linearGradient>
        </defs>
        <!-- Background circle -->
        <circle class="progress-ring-circle progress-ring-bg" cx="33" cy="33" r="30"></circle>
        <!-- Progress circle -->
        <circle id="progress-ring-fill" class="progress-ring-circle progress-ring-fill"
                cx="33" cy="33" r="30"
                stroke-dasharray="188.5"
                stroke-dashoffset="188.5"></circle>
      </svg>
      <span class="progress-badge" id="progress-badge">0%</span>
    </button>

    <!-- Milestone Celebration Modal -->
    <div id="milestone-modal" class="milestone-modal">
      <div class="milestone-icon" id="milestone-icon">🎉</div>
      <h2 class="milestone-title" id="milestone-title">Milestone Reached!</h2>
      <p class="milestone-message" id="milestone-message">Great progress!</p>
      <button class="milestone-close" id="milestone-close">Continue Learning</button>
    </div>

    <!-- Confetti Container -->
    <div id="confetti-container" class="confetti-container"></div>

    <!-- Side Panel -->
    <div id="progress-panel" class="progress-panel">
      <div class="progress-panel-header">
        <h3>📊 Learning Progress</h3>
        <button id="progress-panel-close" class="progress-panel-close" title="Close">&times;</button>
      </div>

      <div class="progress-panel-content">
        <div class="progress-overall-section">
          <div class="progress-stats">
            <span class="progress-count" id="overall-progress-text">0 / 0</span>
            <span class="progress-percentage" id="overall-progress-pct">0%</span>
          </div>
          <div class="progress-bar-wrapper">
            <div class="progress-bar-fill" id="overall-progress-fill"></div>
          </div>
          <p class="progress-subtitle">Total Documentation Pages</p>
        </div>

        <div class="progress-categories-section">
          <h4>By Category</h4>
          <div id="progress-categories"></div>
        </div>

        <button id="progress-reset-btn" class="progress-reset-btn-panel">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
            <path d="M21 3v5h-5"></path>
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
            <path d="M3 21v-5h5"></path>
          </svg>
          Reset Progress
        </button>
      </div>
    </div>

    <!-- Overlay -->
    <div id="progress-overlay" class="progress-overlay"></div>
  `;

  // Insert at end of body
  document.body.insertAdjacentHTML('beforeend', progressHTML);

  // Add event listeners
  document.getElementById('progress-float-btn').addEventListener('click', openProgressPanel);
  document.getElementById('progress-panel-close').addEventListener('click', closeProgressPanel);
  document.getElementById('progress-overlay').addEventListener('click', closeProgressPanel);
  document.getElementById('progress-reset-btn').addEventListener('click', resetProgress);
  document.getElementById('milestone-close').addEventListener('click', closeMilestoneModal);
}

function openProgressPanel() {
  document.getElementById('progress-panel').classList.add('open');
  document.getElementById('progress-overlay').classList.add('visible');
  document.body.style.overflow = 'hidden';
}

function closeProgressPanel() {
  document.getElementById('progress-panel').classList.remove('open');
  document.getElementById('progress-overlay').classList.remove('visible');
  document.body.style.overflow = '';
}

function updateProgressDisplay() {
  const progress = getProgress();
  const stats = calculateProgress(progress);

  const percentage = Math.round(stats.overall.percentage);

  // Get old percentage for milestone checking
  const oldPercentage = parseFloat(localStorage.getItem('last_percentage') || '0');
  localStorage.setItem('last_percentage', percentage.toString());

  // Update floating button badge with pulse
  const badge = document.getElementById('progress-badge');
  if (badge) {
    badge.textContent = percentage + '%';
    // Trigger pulse animation
    badge.classList.remove('pulse');
    void badge.offsetWidth; // Force reflow
    badge.classList.add('pulse');
  }

  // Update circular progress ring
  const progressRing = document.getElementById('progress-ring-fill');
  if (progressRing) {
    const circumference = 2 * Math.PI * 30; // radius = 30
    const offset = circumference - (percentage / 100) * circumference;
    progressRing.style.strokeDashoffset = offset;
  }

  // Update header progress bar
  const headerFill = document.getElementById('header-progress-fill');
  if (headerFill) {
    headerFill.style.width = percentage + '%';
  }

  // Update overall progress in panel
  const overallFill = document.getElementById('overall-progress-fill');
  const overallText = document.getElementById('overall-progress-text');
  const overallPct = document.getElementById('overall-progress-pct');

  if (overallFill) {
    overallFill.style.width = percentage + '%';
  }

  if (overallText) {
    overallText.textContent = `${stats.overall.completed} / ${stats.overall.total}`;
  }

  if (overallPct) {
    overallPct.textContent = percentage + '%';
  }

  // Update category progress
  const categoriesContainer = document.getElementById('progress-categories');
  if (categoriesContainer) {
    categoriesContainer.innerHTML = '';

    Object.entries(stats.categories).forEach(([key, cat]) => {
      const catPercentage = Math.round(cat.percentage);
      const categoryHTML = `
        <div class="progress-category">
          <div class="progress-category-header">
            <span class="progress-category-name">${cat.name}</span>
            <span class="progress-category-count">${cat.completed}/${cat.total}</span>
          </div>
          <div class="progress-bar-wrapper small">
            <div class="progress-bar-fill" style="width: ${catPercentage}%"></div>
          </div>
        </div>
      `;
      categoriesContainer.insertAdjacentHTML('beforeend', categoryHTML);
    });
  }

  // Check for milestones
  checkMilestones(oldPercentage, percentage);
}

function calculateProgress(progress) {
  const stats = {
    overall: { completed: 0, total: 0, percentage: 0 },
    categories: {}
  };

  Object.entries(DOC_STRUCTURE).forEach(([key, category]) => {
    const total = category.pages.length;
    const completed = category.pages.filter(page =>
      progress.visitedPages.includes(page)
    ).length;

    stats.categories[key] = {
      name: category.name,
      completed: completed,
      total: total,
      percentage: total > 0 ? (completed / total) * 100 : 0
    };

    stats.overall.completed += completed;
    stats.overall.total += total;
  });

  stats.overall.percentage = stats.overall.total > 0
    ? (stats.overall.completed / stats.overall.total) * 100
    : 0;

  return stats;
}

function checkMilestones(oldPercentage, newPercentage) {
  const milestones = [25, 50, 75, 100];
  const shownMilestones = JSON.parse(localStorage.getItem('shown_milestones') || '[]');

  for (const milestone of milestones) {
    // Check if we just reached this milestone and haven't shown it yet
    if (oldPercentage < milestone && newPercentage >= milestone && !shownMilestones.includes(milestone)) {
      showMilestoneModal(milestone);
      shownMilestones.push(milestone);
      localStorage.setItem('shown_milestones', JSON.stringify(shownMilestones));
      break; // Show only one milestone at a time
    }
  }
}

function showMilestoneModal(percentage) {
  const milestones = {
    25: { icon: '🌟', title: 'Quarter Way There!', message: '25% complete!' },
    50: { icon: '🎯', title: 'Halfway Champion!', message: '50% complete!' },
    75: { icon: '🚀', title: 'Almost There!', message: '75% complete!' },
    100: { icon: '🏆', title: 'Documentation Master!', message: '100% complete!' }
  };

  const milestone = milestones[percentage];
  if (!milestone) return;

  const modal = document.getElementById('milestone-modal');
  const icon = document.getElementById('milestone-icon');
  const title = document.getElementById('milestone-title');
  const message = document.getElementById('milestone-message');

  if (modal && icon && title && message) {
    icon.textContent = milestone.icon;
    title.textContent = milestone.title;
    message.textContent = milestone.message;

    modal.classList.add('show');

    // Launch confetti for 100%
    if (percentage === 100) {
      launchConfetti();
    }

    // Auto-close after 5 seconds
    setTimeout(() => {
      closeMilestoneModal();
    }, 5000);
  }
}

function closeMilestoneModal() {
  const modal = document.getElementById('milestone-modal');
  if (modal) {
    modal.classList.remove('show');
  }
}

function launchConfetti() {
  const container = document.getElementById('confetti-container');
  if (!container) return;

  const colors = ['#0078D4', '#00D9C0', '#FFD700', '#FF6B9D', '#C471ED', '#12D8FA'];
  const confettiCount = 150;

  for (let i = 0; i < confettiCount; i++) {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    confetti.style.left = Math.random() * 100 + '%';
    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    confetti.style.animationDelay = Math.random() * 0.5 + 's';
    confetti.style.animationDuration = (Math.random() * 1 + 2) + 's';

    container.appendChild(confetti);

    // Trigger animation
    setTimeout(() => {
      confetti.classList.add('active');
    }, 10);

    // Remove after animation
    setTimeout(() => {
      confetti.remove();
    }, 3500);
  }
}

function resetProgress() {
  if (confirm('Are you sure you want to reset all progress?')) {
    localStorage.removeItem(PROGRESS_STORAGE_KEY);
    localStorage.removeItem('last_percentage');
    localStorage.removeItem('shown_milestones');
    updateProgressDisplay();
    console.log('Progress reset');
  }
}

// ============================================================================
// CONTACT PANEL - Quick access to support channels
// ============================================================================

function initContactPanel() {
  // Create and inject contact button and panel
  createContactPanel();
}

function createContactPanel() {
  // Check if contact panel already exists
  if (document.getElementById('contact-float-btn')) return;

  const contactHTML = `
    <!-- Floating Contact Button -->
    <button id="contact-float-btn" class="contact-float-btn" title="Contact & Support">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
    </button>

    <!-- Contact Side Panel -->
    <div id="contact-panel" class="contact-panel">
      <div class="contact-panel-header">
        <h3>💬 Contact & Support</h3>
        <button id="contact-panel-close" class="contact-panel-close" title="Close">&times;</button>
      </div>

      <div class="contact-panel-content">
        <div class="contact-intro">
          <h4>Need Help?</h4>
          <p>Have questions about PyMT5 SDK? Reach out to us through your preferred messenger!</p>
        </div>

        <div class="contact-buttons">
          <!-- Telegram Button -->
          <a href="https://t.me/MetaRPC_Support" target="_blank" class="contact-btn contact-btn-telegram">
            <div class="contact-btn-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161l-1.84 8.673c-.139.622-.502.775-.998.483l-2.764-2.037-1.332 1.282c-.147.147-.271.271-.556.271l.199-2.815 5.139-4.643c.224-.199-.048-.31-.347-.111l-6.355 4.003-2.737-.856c-.595-.187-.607-.595.125-.881l10.703-4.124c.496-.182.93.114.762.877z"/>
              </svg>
            </div>
            <div class="contact-btn-content">
              <div class="contact-btn-title">Telegram</div>
              <div class="contact-btn-desc">Quick responses & community chat</div>
            </div>
          </a>

          <!-- WhatsApp Button -->
          <a href="https://wa.me/79956432506" target="_blank" class="contact-btn contact-btn-whatsapp">
            <div class="contact-btn-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
            </div>
            <div class="contact-btn-content">
              <div class="contact-btn-title">WhatsApp</div>
              <div class="contact-btn-desc">Direct messaging & voice calls</div>
            </div>
          </a>

          <!-- GitHub Discussions Button -->
          <a href="https://github.com/Moongoord/MetaRPC-Gateway-Support" target="_blank" class="contact-btn contact-btn-github">
            <div class="contact-btn-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </div>
            <div class="contact-btn-content">
              <div class="contact-btn-title">GitHub Discussions</div>
              <div class="contact-btn-desc">Community support & Q&A</div>
            </div>
          </a>

          <!-- Email Button -->
          <a href="mailto:metarpc.helpers@gmail.com" class="contact-btn contact-btn-email">
            <div class="contact-btn-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
            </div>
            <div class="contact-btn-content">
              <div class="contact-btn-title">Email</div>
              <div class="contact-btn-desc">Business inquiries & partnerships</div>
            </div>
          </a>
        </div>
      </div>
    </div>

    <!-- Contact Overlay -->
    <div id="contact-overlay" class="progress-overlay"></div>
  `;

  // Insert at end of body
  document.body.insertAdjacentHTML('beforeend', contactHTML);

  // Add event listeners
  document.getElementById('contact-float-btn').addEventListener('click', openContactPanel);
  document.getElementById('contact-panel-close').addEventListener('click', closeContactPanel);
  document.getElementById('contact-overlay').addEventListener('click', closeContactPanel);
}

function openContactPanel() {
  document.getElementById('contact-panel').classList.add('open');
  document.getElementById('contact-overlay').classList.add('visible');
  document.body.style.overflow = 'hidden';
}

function closeContactPanel() {
  document.getElementById('contact-panel').classList.remove('open');
  document.getElementById('contact-overlay').classList.remove('visible');
  document.body.style.overflow = '';
}
