<template>
    <div>
        <div class="table-pagination">
            <ul class="pagination">
                <li class="page-item">
                    <button class="page-link" @click="fnFirstPage">
                        <span aria-hidden="true">Первая</span>
                    </button>
                </li>
                <li class="page-item">
                    <button class="page-link" @click="fnPreviousPage">
                        <span aria-hidden="true">Предыдущая</span>
                    </button>
                </li>
                <li class="page-item page-number">
                    <input type="text" v-model="oPage.iPage"/>
                    <button class="btn btn-light" @click="fnReload">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </li>
                <li class="page-item">
                    <button class="page-link" @click="fnNextPage">
                        <span aria-hidden="true">Следующая</span>
                    </button>
                </li>
                <li class="page-item">
                    <button class="page-link" @click="fnLastPage">
                        <span aria-hidden="true">Последняя</span>
                    </button>
                </li>
            </ul>

            <div class="actions-panel">
                <div class="btn-group" role="group">
                    <button @click="fnDeleteItem" type="button" class="btn btn-light"><i class="bi bi-trash-fill"></i></button>
                    <button @click="fnEditItem" type="button" class="btn btn-light"><i class="bi bi-pencil"></i></button>
                    <button @click="fnNewItem" type="button" class="btn btn-light"><i class="bi bi-plus-lg"></i></button>
                </div>
            </div>
        </div>
        <div class="table">
            <div class="table-row">
                <div class="table-cell table-cell-header">
                    Превью
                </div>
                <div class="table-cell table-cell-header">
                    Название
                    <input type="text" class="form-control" v-model="oPage.oFilters.name" @input="$fetch">
                </div>
                <div class="table-cell table-cell-header">
                    Описание
                    <input type="text" class="form-control" v-model="oPage.oFilters.description" @input="$fetch">
                </div>
            </div>
            <template v-for="oBook in aBooks">
                <div 
                    :class="'table-row '+((oSelectedItem && oSelectedItem.id==book.id) ? 'active':'')"
                    @click="fnSelectItem(oBook)"
                >
                    <div class="table-cell">
                        <img 
                            v-if="oBook.thumbnail" 
                            class="table-book-thumbnail"
                            :src="'/assets/thumbnails/'+oBook.thumbnail" 
                        />
                    </div>
                    <div class="table-cell">
                        <router-link :to="'/book/'+oBook.id">
                        {{ oBook.name }}
                        </router-link>
                    </div>
                    <div class="table-cell">{{ oBook.description }}</div>
                </div>
            </template>
        </div>

        <div class="" v-if="bShowEditWindow">
            <div class="overlay"></div>
            <div class="modal show" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Редактировать</h5>
                            <button 
                                type="button" 
                                class="btn-close" 
                                data-bs-dismiss="modal" 
                                aria-label="Close"
                                @click="fnCloseEditWindow"
                            ></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label>Название</label>
                                <input class="form-control" v-model="oItem.name">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Описание</label>
                                <textarea 
                                    class="form-control" 
                                    v-model="oItem.description"
                                    rows="10"
                                ></textarea>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button 
                                type="button" 
                                class="btn btn-secondary" 
                                data-bs-dismiss="modal"
                                @click="fnCloseEditWindow"
                            >Close</button>
                            <button 
                                type="button" 
                                class="btn btn-primary"
                                @click="fnSaveEditWindow"
                            >Save</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        this.axios.get("books").then((response) => {
            console.log(response.data)
        })
        return {
            oPage: {
                oFilters: {
                    name: "",
                    description: "",
                },
                oSorts: {
                    name: false,
                    description: false
                },
                iPage: 1,
                iPagesCount: 1,
            },
            oItem: {
                name: "",
                description: "",
            },
            bShowEditWindow: false,
            aBooks: [],
            oSelectedItem: null,
        };
    },
    // async fetch() {
    //     console.log(this.oPage.oFilters.name)

    //     this.axios.get("books").then((response) => {
    //         console.log(response.data)
    //     })
        
    //     // var { aList, iPagesCount } = await this.$api("books", "fnGetPage", this.oPage);
    //     // this.books = aList;
    //     // this.oPage.iPagesCount = iPagesCount;
    // },
    watch: {
        'oPage.iPage': function (mN, mO) {
            this.$fetch()
        }
    },
    methods: {
        fnNextPage() { 
            this.oPage.iPage++
            if (this.oPage.iPage>this.oPage.iPagesCount) 
                this.oPage.iPage = this.oPage.iPagesCount
        },
        fnPreviousPage() { 
            this.oPage.iPage--
            if (this.oPage.iPage<1) 
                this.oPage.iPage = 1
        },
        fnFirstPage() {
            this.oPage.iPage = 1
        },
        fnLastPage() {
            this.oPage.iPage = this.oPage.iPagesCount
        },
        fnReload() {
            this.$fetch()
        },
        fnSelectItem(oItem) {
            this.oSelectedItem = oItem
        },
        fnShowEditWindow() {
            this.bShowEditWindow = true
        },
        fnCloseEditWindow() {
            this.bShowEditWindow = false
        },
        async fnDeleteItem() {
            if (!this.oSelectedItem) { return alert("Нужно выбрать!") }
            await this.$api("books", "fnDeleteBook", this.oSelectedItem.id)
        },
        fnEditItem() {
            if (!this.oSelectedItem) { return alert("Нужно выбрать!") }
            this.oItem = this.oSelectedItem
            this.fnShowEditWindow()
        },
        fnNewItem() {
            this.oItem.id = 0
            this.oItem.name = ""
            this.oItem.description = ""
            this.fnShowEditWindow()
        },
        async fnSaveEditWindow() {
            if (this.oItem.id) {
                await this.$api("books", "fnUpdateBook", this.oItem)
            } else {
                await this.$api("books", "fnAddBook", this.oItem)
            }
            this.fnCloseEditWindow()
        }
    },

    created() {

    }
};
</script>

<style>
.table-row {
    grid-template-columns: 100px 1fr 2fr;
}
</style>
