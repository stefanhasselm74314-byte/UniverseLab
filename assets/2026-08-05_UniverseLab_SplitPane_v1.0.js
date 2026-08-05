(() => {
  'use strict';

  const BREAKPOINT = 900;
  const STORAGE_PREFIX = 'universelab:split-pane:v1:';
  const MOBILE_QUERY = window.matchMedia(`(max-width:${BREAKPOINT}px)`);

  const number = (value, fallback) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  const safeStorage = {
    get(key) {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
      } catch {
        return null;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch {
        // Layout persistence is optional; the workspace remains functional.
      }
    },
    remove(key) {
      try {
        localStorage.removeItem(key);
      } catch {
        // Ignore unavailable storage.
      }
    }
  };

  const scheduleLayoutEvent = (() => {
    let frame = 0;
    return root => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        root.dispatchEvent(new CustomEvent('universelab:split-pane-change', { bubbles: true }));
        window.dispatchEvent(new Event('resize'));
      });
    };
  })();

  function initialize(root) {
    if (root.dataset.ulSplitInitialized === 'true') return;

    const startPane = root.querySelector(':scope > [data-ul-pane="start"]');
    const endPane = root.querySelector(':scope > [data-ul-pane="end"]');
    if (!startPane || !endPane) return;

    const key = root.dataset.ulSplitKey || `workspace-${document.querySelectorAll('[data-ul-split]').length}`;
    const storageKey = `${STORAGE_PREFIX}${key}`;
    const label = root.dataset.ulSplitLabel || 'Seitenpanel';
    const defaultWidth = number(root.dataset.ulSplitDefault, 320);
    const minimumWidth = number(root.dataset.ulSplitMin, 240);
    const configuredMaximum = number(root.dataset.ulSplitMax, 560);
    const endMinimum = number(root.dataset.ulSplitEndMin, 420);

    const stored = safeStorage.get(storageKey) || {};
    const state = {
      width: number(stored.width, defaultWidth),
      collapsed: stored.collapsed === true
    };

    const toolbar = document.createElement('div');
    toolbar.className = 'ul-split-controls';
    toolbar.dataset.ulSplitControls = key;
    toolbar.setAttribute('aria-label', `${label}-Layout`);

    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.dataset.ulSplitAction = 'toggle';

    const resetButton = document.createElement('button');
    resetButton.type = 'button';
    resetButton.dataset.ulSplitAction = 'reset';
    resetButton.textContent = 'Layout zurücksetzen';

    const hint = document.createElement('span');
    hint.className = 'ul-split-hint';
    hint.textContent = 'Trennlinie ziehen · Pfeiltasten für Feineinstellung · Doppelklick setzt zurück';

    const status = document.createElement('output');
    status.className = 'ul-split-status';
    status.setAttribute('aria-live', 'polite');

    toolbar.append(toggleButton, resetButton, hint, status);
    root.before(toolbar);

    const separator = document.createElement('div');
    separator.className = 'ul-splitter';
    separator.tabIndex = 0;
    separator.setAttribute('role', 'separator');
    separator.setAttribute('aria-orientation', 'vertical');
    separator.setAttribute('aria-label', `${label} skalieren`);
    root.insertBefore(separator, endPane);

    root.classList.add('ul-split-ready');
    root.dataset.ulSplitInitialized = 'true';

    const bounds = () => {
      const total = Math.max(root.getBoundingClientRect().width, minimumWidth + endMinimum + 12);
      const maximum = Math.max(minimumWidth, Math.min(configuredMaximum, total - endMinimum - 12));
      return { minimum: minimumWidth, maximum };
    };

    const persist = () => safeStorage.set(storageKey, {
      width: Math.round(state.width),
      collapsed: state.collapsed
    });

    const apply = ({ save = false, announce = false } = {}) => {
      const { minimum, maximum } = bounds();
      state.width = clamp(state.width, minimum, maximum);

      root.style.setProperty('--ul-split-start', `${Math.round(state.width)}px`);
      root.classList.toggle('ul-split-collapsed', state.collapsed && !MOBILE_QUERY.matches);

      separator.setAttribute('aria-valuemin', String(Math.round(minimum)));
      separator.setAttribute('aria-valuemax', String(Math.round(maximum)));
      separator.setAttribute('aria-valuenow', String(Math.round(state.width)));
      separator.setAttribute('aria-expanded', String(!state.collapsed));

      toggleButton.textContent = state.collapsed ? `${label} anzeigen` : `${label} ausblenden`;
      toggleButton.setAttribute('aria-pressed', String(state.collapsed));
      status.value = state.collapsed && !MOBILE_QUERY.matches
        ? `${label}: ausgeblendet`
        : `${label}: ${Math.round(state.width)} px`;
      status.textContent = status.value;

      if (save) persist();
      if (announce) status.focus?.();
      scheduleLayoutEvent(root);
    };

    const reset = () => {
      state.width = defaultWidth;
      state.collapsed = false;
      safeStorage.remove(storageKey);
      apply({ save: true });
    };

    const toggle = () => {
      state.collapsed = !state.collapsed;
      apply({ save: true });
    };

    toggleButton.addEventListener('click', toggle);
    resetButton.addEventListener('click', reset);
    separator.addEventListener('dblclick', reset);

    let drag = null;

    separator.addEventListener('pointerdown', event => {
      if (MOBILE_QUERY.matches) return;
      if (state.collapsed) {
        toggle();
        return;
      }
      if (event.button !== 0 && event.pointerType === 'mouse') return;

      drag = {
        pointerId: event.pointerId,
        startX: event.clientX,
        startWidth: state.width
      };
      separator.setPointerCapture?.(event.pointerId);
      document.body.classList.add('ul-split-dragging');
      event.preventDefault();
    });

    separator.addEventListener('pointermove', event => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      state.width = drag.startWidth + (event.clientX - drag.startX);
      apply();
    });

    const stopDrag = event => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      drag = null;
      document.body.classList.remove('ul-split-dragging');
      persist();
      scheduleLayoutEvent(root);
    };

    separator.addEventListener('pointerup', stopDrag);
    separator.addEventListener('pointercancel', stopDrag);
    separator.addEventListener('lostpointercapture', event => {
      if (drag && drag.pointerId === event.pointerId) {
        drag = null;
        document.body.classList.remove('ul-split-dragging');
        persist();
      }
    });

    separator.addEventListener('keydown', event => {
      if (MOBILE_QUERY.matches) return;
      const { minimum, maximum } = bounds();
      const step = event.shiftKey ? 40 : 12;
      let handled = true;

      switch (event.key) {
        case 'ArrowLeft':
          state.collapsed = false;
          state.width -= step;
          break;
        case 'ArrowRight':
          state.collapsed = false;
          state.width += step;
          break;
        case 'Home':
          state.collapsed = false;
          state.width = minimum;
          break;
        case 'End':
          state.collapsed = false;
          state.width = maximum;
          break;
        case 'Enter':
        case ' ':
          toggle();
          break;
        default:
          handled = false;
      }

      if (!handled) return;
      event.preventDefault();
      if (event.key !== 'Enter' && event.key !== ' ') apply({ save: true });
    });

    const resizeObserver = new ResizeObserver(() => apply());
    resizeObserver.observe(root);

    const mediaChange = () => apply();
    MOBILE_QUERY.addEventListener?.('change', mediaChange);

    apply();
  }

  const start = () => document.querySelectorAll('[data-ul-split]').forEach(initialize);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();
