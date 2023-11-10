odoo.define('stock_fefo.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    var models = require('point_of_sale.models');


    models.load_fields('product.product', 'removal_strategy_id');
    models.load_fields('product.category', 'removal_strategy_id');
    models.load_models([{
        model:  'product.removal',
        fields: ['name', 'id', 'method'],
        loaded: function(self, removals){
            self.removals = removals;
        },
    }]);

    const PosFEFOProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _getAddProductOptions(product) {
                let self = this;
                let price_extra = 0.0;
                let draftPackLotLines, weight, description, packLotLinesToEdit;

                if (this.env.pos.config.product_configurator && _.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
                    let attributes = _.map(product.attribute_line_ids, (id) => this.env.pos.attributes_by_ptal_id[id])
                                      .filter((attr) => attr !== undefined);
                    let { confirmed, payload } = await this.showPopup('ProductConfiguratorPopup', {
                        product: product,
                        attributes: attributes,
                    });

                    if (confirmed) {
                        description = payload.selected_attributes.join(', ');
                        price_extra += payload.price_extra;
                    } else {
                        return;
                    }
                }

                // Gather lot information if required.
                if (['serial', 'lot'].includes(product.tracking) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                    let confirm = false;
                    if (this.env.pos.config.auto_select_lots && (product.removal_strategy_id.length || product.categ.removal_strategy_id.length)) {
                        // automatic selection lot
                        var removal = this.env.pos.removals.find(rm => rm.id === product.removal_strategy_id[0])
                        if (!removal) {
                            removal = this.env.pos.removals.find(rm => rm.id === product.categ.removal_strategy_id[0])
                        }

                        let lotId = await this.rpc({
                            model: 'product.product',
                            method: 'get_lot_id',
                            args: [product.id, self.env.pos.config.id],
                        });
                        if (lotId) {
                            var payload = [{
                                    text: lotId,
                                    _id: 0,
                                }];
                            var confirmed = true;
                        } else {
                            var confirmed = false;
                        }
                        confirm = confirmed;
                        if (confirmed) {
                            // Segregate the old and new packlot lines
                            const modifiedPackLotLines = Object.fromEntries(
                                payload.filter(item => item.id).map(item => [item.id, item.text])
                            );
                            const newPackLotLines = payload
                                .filter(item => !item.id)
                                .map(item => ({ lot_name: item.text }));

                            draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                        }
                        // else: We proceed on adding product without lot
                    } else {
                        // Manual selection lot and serie
                        const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
                        if (isAllowOnlyOneLot) {
                            packLotLinesToEdit = [];
                        } else {
                            const orderline = this.currentOrder
                                .get_orderlines()
                                .filter(line => !line.get_discount())
                                .find(line => line.product.id === product.id);
                            if (orderline) {
                                packLotLinesToEdit = orderline.getPackLotLinesToEdit();
                            } else {
                                packLotLinesToEdit = [];
                            }
                        }
                        const { confirmed, payload } = await this.showPopup('EditListPopup', {
                            title: this.env._t('Lot/Serial Number(s) Required'),
                            isSingleItem: isAllowOnlyOneLot,
                            array: packLotLinesToEdit,
                        });
                        confirm = confirmed;
                        if (confirmed) {
                        // Segregate the old and new packlot lines
                        const modifiedPackLotLines = Object.fromEntries(
                            payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
                        );
                        const newPackLotLines = payload.newArray
                            .filter(item => !item.id)
                            .map(item => ({ lot_name: item.text }));

                        draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                        } else {
                            // We don't proceed on adding product.
                            return;
                        }
                    }
                    confirmed = confirm;
                }

                // Take the weight if necessary.
                if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
                    // Show the ScaleScreen to weigh the product.
                    if (this.isScaleAvailable) {
                        const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
                            product,
                        });
                        if (confirmed) {
                            weight = payload.weight;
                        } else {
                            // do not add the product;
                            return;
                        }
                    } else {
                        await this._onScaleNotAvailable();
                    }
                }

                return { draftPackLotLines, quantity: weight, description, price_extra };
            }
        };

    Registries.Component.extend(ProductScreen, PosFEFOProductScreen);

    return ProductScreen;
});
