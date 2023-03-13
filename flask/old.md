```
# @app.route("/books", defaults={"page": 1})
# @app.route("/books/<int:page>")

# context['books'] = []
# # search=False
# page, per_page, offset = get_page_args()

# per_page = 10
# # books = Book.query.all()
# # books = Book.query.paginate(page, 10, True)
# books = Book.query.limit(per_page).offset(offset)
# total = Book.query.count()
# pagination = Pagination(
#     page=page, 
#     per_page=per_page, 
#     total = total,        
#     format_total=True,  
#     format_number=True,  
#     record_name='books',
#     # search=search, 
#     css_framework='bootstrap4'
# )
# table = TableBooks(books, no_items='')
# context['table']=table
# context['pagination']=pagination
```

```
<!-- <div class="pagination-wrapper">
    <div class="pagination-block">
        {{ context.pagination.links }}
    </div>
</div>
{{ context.table }} -->

<!-- <form action="">
<div>
    <div class="table-pagination">
        <ul class="pagination">
            <li class="page-item">
                <a class="page-link" href="/books/{{context.page_first}}">
                    <span aria-hidden="true">Первая</span>
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="/books/{{context.page_prev}}">
                    <span aria-hidden="true">Предыдущая</span>
                </a>
            </li>
            <li class="page-item page-number">
                <input type="text" name="page" value="{{context.page}}"/>
            </li>
            <li class="page-item">
                <a class="page-link" href="/books/{{context.page_next}}">
                    <span aria-hidden="true">Следующая</span>
                </a>
            </li>
            <li class="page-item">
                <a class="page-link" href="/books/{{context.page_last}}">
                    <span aria-hidden="true">Последняя</span>
                </a>
            </li>
        </ul>
    </div>
    <div class="table">
        <div class="table-row">
            <div class="table-cell table-cell-header">
                Превью
            </div>
            <div class="table-cell table-cell-header">
                Название
                <input type="text" class="form-control">
            </div>
            <div class="table-cell table-cell-header">
                Описание
                <input type="text" class="form-control">
            </div>
            <div class="table-cell table-cell-header"></div>
        </div>
        {% for book in context.books %}
        <div 
            class="table-row"
        >
            <div class="table-cell">
                <img 
                    class="table-book-thumbnail img-thumbnail"
                    src="{{ book.preview }}" 
                    onerror="e.target.src='/static/noimg.jpg'"
                />
            </div>
            <div class="table-cell">
                {{ book.name }}
            </div>
            <div class="table-cell">{{ book.description }}</div>
            <div class="table-cell">
                <div class="btn-group" role="group">
                    <button name="delete" value="1" type="button" class="btn btn-light"><i class="bi bi-trash-fill"></i></button>
                    <button name="edit" value="1" type="button" class="btn btn-light"><i class="bi bi-pencil"></i></button>
                </div>        
            </div>
        </div>
        {% endfor %}
    </div>
</div>
</form>

<style>
.table-row {
    grid-template-columns: 100px 1fr 2fr 160px;
}
</style> -->
```