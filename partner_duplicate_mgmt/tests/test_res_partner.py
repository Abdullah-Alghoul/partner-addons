# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common
from openerp.exceptions import UserError


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.partner_1 = cls.env['res.partner'].create({
            'name': '11 Big Partner inc.',
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'My Partner inc.',
        })
        cls.partner_3 = cls.env['res.partner'].create({
            'name': '33 Big Partner',
        })

    def test_01_partner_indexed_name(self):
        self.assertEqual(self.partner_1.indexed_name, 'big partner')

        self.partner_1.write({'name': '123 CANADA Pince'})
        self.assertEqual(self.partner_1.indexed_name, 'pince')

    def test_02_create_new_partner_compute_duplicates(self):
        self.assertTrue(self.partner_3.duplicate_ids)
        self.assertEqual(self.partner_3.duplicate_count, 1)
        self.assertIn(self.partner_1, self.partner_3.duplicate_ids)

        self.assertIn(self.partner_1.name, self.partner_3.message_ids[0].body)

    def test_03_edit_partner_compute_duplicates(self):
        self.assertEqual(self.partner_2.duplicate_count, 0)

        self.partner_2.write({'name': '22 Bigg Partner'})
        self.assertTrue(self.partner_2.duplicate_ids)
        self.assertEqual(self.partner_2.duplicate_count, 2)
        self.assertIn(self.partner_1, self.partner_2.duplicate_ids)
        self.assertIn(self.partner_3, self.partner_2.duplicate_ids)

        self.assertIn(
            '11 Big Partner inc.', self.partner_2.message_ids[0].body)
        self.assertIn('33 Big Partner', self.partner_2.message_ids[0].body)

    def test_04_should_not_select_more_than_2_partners_to_merge(self):
        partners = self.partner_1 | self.partner_2 | self.partner_3
        with self.assertRaises(UserError):
            partners.action_merge()

    def test_05_should_not_create_new_duplicate_line(self):
        partners = self.partner_1 | self.partner_3
        partners.action_merge()
        duplicates = self.env['res.partner.duplicate'].search([
            ('partner_1_id', 'in', partners.ids),
            ('partner_2_id', 'in', partners.ids),
        ])
        self.assertEqual(len(duplicates), 1)

    def test_06_merge_selected_contacts_action_is_unlinked(self):
        action = self.env['ir.actions.act_window'].search([
            ('name', '=', 'Merge Selected Contacts')])
        self.assertFalse(action)
