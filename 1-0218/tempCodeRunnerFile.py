for item in news_items:
        link_tag = item.find_parent('a', href=True)
        title = item.get_text(strip=True)
        if link_tag is None or not title or '快訊' not in title:
            continue