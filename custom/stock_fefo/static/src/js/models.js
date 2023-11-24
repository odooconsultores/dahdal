odoo.define('stock_fefo.models', function (require) {
"use strict";

var models = require('point_of_sale.models');


var _super_orderline = models.Orderline.prototype;
var _super_order = models.Order.prototype;


var PacklotlineCollection = Backbone.Collection.extend({
    model: models.Packlotline,
    initialize: function(models, options) {
        this.order_line = options.order_line;
    },

    get_valid_lots: function(){
        return this.filter(function(model){
            return model.get('lot_name');
        });
    },

    set_quantity_by_lot: function() {
        let quantity = this.order_line.quantity;
        var valid_lots_quantity = this.get_valid_lots().length;
        if (this.order_line.quantity < 0){
            valid_lots_quantity = -valid_lots_quantity;
        }
        this.order_line.set_quantity(quantity);
    }
});

models.Orderline = models.Orderline.extend({
//    set_product_lot: function(product){
//        this.has_product_lot = product.tracking !== 'none';
//        this.pack_lot_lines  = this.has_product_lot && new PacklotlineCollection(null, {'order_line': this});
//    },
    initialize: function(attr,options){
        _super_orderline.initialize.apply(this,arguments);
        this.availables_lots = [];
//        if (options.quantity) {
//            this.set_quantity(options.quantity);
//        }
    },

    has_valid_quantity_lot: function(){
        if(!this.has_product_lot){
            return true;
        }
        let lot_names = this.pack_lot_lines.models.length ? this.pack_lot_lines.models[0].attributes.lot_name : '';
        let max_quantity = this.availables_lots ? this.availables_lots.filter(l => lot_names.includes(l[0])) : [];
        max_quantity = max_quantity.length ? max_quantity[0][1] : this.quantity;
        return max_quantity < this.quantity;
    },

    divide_quantity: function(){
        let quantity = this.quantity
        this.set_quantity(quantity);
        this.order.assert_editable();
        let lot_names = this.pack_lot_lines.models.length ? this.pack_lot_lines.models[0].attributes.lot_name : '';
        let max_quantity = this.availables_lots ? this.availables_lots.filter(l => lot_names.includes(l[0])) : [];
        max_quantity = max_quantity.length ? max_quantity[0][1] : quantity
        if(quantity > max_quantity){
            let draftPackLotLines;
//            this.quantity = max_quantity
            this.set_quantity(max_quantity);
//            this.quantityStr = '' + this.quantity;
            let availables_lots = this.availables_lots.filter(l => !lot_names.includes(l[0]));
            if (availables_lots.length) {
                var payload = [{
                        text: availables_lots[0][0],
                        _id: 0,
                    }];
                const modifiedPackLotLines = Object.fromEntries(
                    payload.filter(item => item.id).map(item => [item.id, item.text])
                );
                const newPackLotLines = payload
                    .filter(item => !item.id)
                    .map(item => ({ lot_name: item.text }));
                draftPackLotLines = { modifiedPackLotLines, newPackLotLines };



                this.order.add_product(this.product, {
                    quantity: quantity - max_quantity,
                    draftPackLotLines: draftPackLotLines,
                    availables_lots: availables_lots,
                    merge: false,
                });
                this.order.selected_orderline.set_quantity(quantity - max_quantity);
                this.order.selected_orderline.divide_quantity();
            }
        }
    },

});


models.Order = models.Order.extend({
    add_product: function(product, options){
        _super_order.add_product.apply(this,arguments);
        this.selected_orderline.availables_lots = options.availables_lots ? options.availables_lots : [];

    },
});

});