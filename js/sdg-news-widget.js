(function () {
  const NEWS_ENDPOINT = 'data/sdg_stream.json';
  const widgetRoot = document.querySelector('[data-widget="sdg-news"]');
  if (!widgetRoot) {
    return;
  }

  const listEl = widgetRoot.querySelector('.sdg-news__list');
  const statusEl = widgetRoot.querySelector('.sdg-news__status');

  function formatPost(post) {
    const container = document.createElement('article');
    container.className = 'sdg-news__item';

    const textEl = document.createElement('p');
    textEl.className = 'sdg-news__text';
    textEl.textContent = post.text;
    container.appendChild(textEl);

    if (post.hashtags && post.hashtags.length > 0) {
      const hashtags = document.createElement('p');
      hashtags.className = 'sdg-news__hashtags';
      hashtags.textContent = post.hashtags.join(' ');
      container.appendChild(hashtags);
    }

    const meta = document.createElement('p');
    meta.className = 'sdg-news__meta';

    const publishedDate = new Date(post.published);
    const formattedDate = publishedDate.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });

    const link = document.createElement('a');
    link.href = post.link || '#';
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Read more';

    meta.append(`${formattedDate} • ${post.source} • `);
    meta.appendChild(link);
    container.appendChild(meta);

    return container;
  }

  function renderSection(title, posts) {
    const section = document.createElement('section');
    section.className = 'sdg-news__section';

    const heading = document.createElement('h3');
    heading.className = 'sdg-news__section-title';
    heading.textContent = title;
    section.appendChild(heading);

    const grid = document.createElement('div');
    grid.className = 'sdg-news__section-grid';
    posts.forEach((post) => {
      grid.appendChild(formatPost(post));
    });
    section.appendChild(grid);

    return section;
  }

  function renderPosts(globalPosts, azmiuPosts) {
    listEl.innerHTML = '';

    if (globalPosts.length > 0) {
      listEl.appendChild(
        renderSection('Global SDG Headlines from Leading Universities', globalPosts),
      );
    }

    if (azmiuPosts.length > 0) {
      listEl.appendChild(
        renderSection('AZMIU Research, Publications, and Patents', azmiuPosts),
      );
    }
  }

  function showError(message) {
    statusEl.textContent = message;
    statusEl.hidden = false;
  }

  function hideStatus() {
    statusEl.hidden = true;
  }

  fetch(NEWS_ENDPOINT, { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((payload) => {
      const globalPosts = Array.isArray(payload.global_posts)
        ? payload.global_posts
        : [];
      const azmiuPosts = Array.isArray(payload.azmiu_posts)
        ? payload.azmiu_posts
        : [];

      if (globalPosts.length === 0 && azmiuPosts.length === 0) {
        showError('No SDG updates available right now. Please check back soon.');
        return;
      }
      hideStatus();
      renderPosts(globalPosts, azmiuPosts);
    })
    .catch(() => {
      showError('Unable to load SDG updates at the moment.');
    });
})();
