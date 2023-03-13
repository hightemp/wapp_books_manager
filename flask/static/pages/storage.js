const updateUrl = (prev, query) => {
    return prev + (prev.indexOf('?') >= 0 ? '&' : '?') + new URLSearchParams(query).toString();
};

(new gridjs.Grid({
    columns: [
        {
            id: 'id',
            name: 'ID',
            hidden: true
        },
        {
            id: 'name',
            name: 'Name'
        },
        {
            name: 'Buttons',
            formatter: (_, row) =>
                gridjs.html(`
                    <a href="/storage/${row.cells[0].data}/edit"><i class="bi bi-pencil"></i></a>
                    <a href="/storage/${row.cells[0].data}/delete"><i class="bi bi-trash"></i></a>
                    <a href="/storage/${row.cells[0].data}/upload"><i class="bi bi-box-arrow-in-up"></i></a>
                `),
            width: "100px"
        }
    ],
    server: {
        url: '/api/storage',
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
                const columnIds = ['name'];
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