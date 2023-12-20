odoo.define('stock_fefo.Orderline', function(require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const PosStockOrderline = Orderline =>
        class extends Orderline {
            lotGenerateLines() {
                this.env.pos.get_order().assert_editable();
                let line = this.props.line;
                line.divide_quantity()
            }
        };

    Registries.Component.extend(Orderline, PosStockOrderline);

    return Orderline;
});
