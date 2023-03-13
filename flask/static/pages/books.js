const updateUrl = (prev, query) => {
    return prev + (prev.indexOf('?') >= 0 ? '&' : '?') + new URLSearchParams(query).toString();
};

(new gridjs.Grid({
    pagination: {
        limit: 6
    },
    columns: [
        { 
            id: 'id',
            name: 'ID',
            hidden: true
        },
        {
            id: 'preview',
            name: 'Preview',
            sort: false,
            formatter: (_, row) => gridjs.html(`
                <a href='/books/${row.cells[0].data}/preview'>
                    <img src="/books/${row.cells[0].data}/preview" onerror="this.src='/static/noimg.jpg'" width="60px"/>
                </a>
            `)
        },
        {
            id: 'name',
            name: 'Name',
            formatter: (_, row) => 
                gridjs.html(`<a href='/books/${row.cells[0].data}/show'>${row.cells[2].data}</a>`)
        },
        {
            id: 'description',
            name: 'Description'
        },
        {
            name: 'Buttons',
            formatter: (_, row) =>
                gridjs.html(`
                    <a href="/books/${row.cells[0].data}/edit"><i class="bi bi-pencil"></i></a>
                    <a href="/books/${row.cells[0].data}/delete"><i class="bi bi-trash"></i></a>
                `),
            width: "100px"
        }
    ],
    server: {
        url: '/api/books',
        then: results => results.data,
        total: results => results.total,
    },
    search: {
        enabled: true,
        server: {
            url: (prev, search) => {
                return updateUrl(prev, {
                    search
                });
            },
        },
    },
    sort: {
        enabled: true,
        multiColumn: true,
        server: {
            url: (prev, columns) => {
                const columnIds = ['name', 'description', 'file', 'preview'];
                const sort = columns.map(col => (col.direction === 1 ? '+' : '-') + columnIds[col.index]);
                return updateUrl(prev, {
                    sort
                });
            },
        },
    },
    pagination: {
        enabled: true,
        server: {
            url: (prev, page, limit) => {
                return updateUrl(prev, {
                    start: page * limit,
                    length: limit
                });
            },
        },
    },
})).render(document.getElementById("table-wrapper"));