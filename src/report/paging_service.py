from sqlalchemy.orm import Session

class PagingService:
    def __init__(self, db: Session):
        self.db = db

    def call(self, *, page, item_per_page, total_item, endpoint) -> dict:
        current_page = int(page)
        has_next_page = (total_item > 0) and (total_item / (current_page * item_per_page) < 1)
        has_prev_page = (total_item > 0) and (current_page > 1)
        next_page_url = (f"{endpoint}?page={current_page + 1}" if has_next_page else None)
        prev_page_url = (f"{endpoint}?page={current_page - 1}" if has_prev_page else None)

        return {
                'page': current_page,
                'total_item': total_item,
                'pagination': {
                    'prev_page_url': prev_page_url,
                    'next_page_url': next_page_url
                }
            }