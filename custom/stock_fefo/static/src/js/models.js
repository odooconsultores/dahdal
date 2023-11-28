odoo.define('stock_fefo.models', function (require) {
"use strict";

var models = require('point_of_sale.models');


var _super_orderline = models.Orderline.prototype;
var _super_order = models.Order.prototype;

var exports = {};


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

exports.Packlotline = Backbone.Model.extend({
    defaults: {
        lot_name: null,
        expiration_date: 'lkdjkfjhs'
    },
    initialize: function(attributes, options){
        this.order_line = options.order_line;
        if (options.json) {
            this.init_from_JSON(options.json);
            return;
        }
    },

    init_from_JSON: function(json) {
        this.order_line = json.order_line;
        console.log('lote')
        console.log(json)
        this.set_lot_name(json.lot_name);
        this.set_expiration_date(json.expiration_date);
    },

    set_expiration_date: function(expiration_date){
        this.set({lot_name : _.str.trim(expiration_date) || null});
    },

    set_lot_name: function(name){
        this.set({lot_name : _.str.trim(name) || null});
    },

    get_lot_name: function(){
        return this.get('lot_name');
    },

    get_expiration_date: function(){
        return this.get('expiration_date');
    },

    export_as_JSON: function(){
        return {
            lot_name: this.get_lot_name(),
        };
    },

    add: function(){
        var order_line = this.order_line,
            index = this.collection.indexOf(this);
        var new_lot_model = new exports.Packlotline({}, {'order_line': this.order_line});
        this.collection.add(new_lot_model, {at: index + 1});
        return new_lot_model;
    },

    remove: function(){
        this.collection.remove(this);
    }
});

models.Orderline = models.Orderline.extend({
    initialize: function(attr,options){
        _super_orderline.initialize.apply(this,arguments);
        this.availables_lots = [];
    },

    setPackLotLines: function({ modifiedPackLotLines, newPackLotLines }) {
        // rewrite the method
        // Set the new values for modified lot lines.
        let lotLinesToRemove = [];
        for (let lotLine of this.pack_lot_lines.models) {
            const modifiedLotName = modifiedPackLotLines[lotLine.cid];
            if (modifiedLotName) {
                lotLine.set({ lot_name: modifiedLotName});
            } else {
                // We should not call lotLine.remove() here because
                // we don't want to mutate the array while looping thru it.
                lotLinesToRemove.push(lotLine);
            }
        }

        // Remove those that needed to be removed.
        for (let lotLine of lotLinesToRemove) {
            lotLine.remove();
        }

        // Create new pack lot lines.
        let newPackLotLine;
        for (let newLotLine of newPackLotLines) {
            newPackLotLine = new exports.Packlotline({}, { order_line: this });
            newPackLotLine.set({ lot_name: newLotLine.lot_name, expiration_date: newLotLine.expiration_date });
            this.pack_lot_lines.add(newPackLotLine);
        }

        // Set the quantity of the line based on number of pack lots.
        if(!this.product.to_weight){
            this.pack_lot_lines.set_quantity_by_lot();
        }
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