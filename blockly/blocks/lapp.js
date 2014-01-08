/**
 * Visual Blocks Editor
 *
 * Copyright 2012 Google Inc.
 * http://blockly.googlecode.com/
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Lapp Procedure blocks for Blockly.
 * @author enavarro222@gmail.com (Emmanuel Navarro)
 */
'use strict';

goog.provide('Blockly.Blocks.lapp');

goog.require('Blockly.Blocks');

//TODO: add tooltips and url

Blockly.Blocks['lapp_setup'] = {
  init: function() {
    //this.setHelpUrl('http://www.example.com/');
    this.setColour(70);
    this.appendDummyInput()
        .appendField(Blockly.Msg.BBLAMP_SETUP_TITLE);
    this.appendStatementInput("STACK")
        .appendField(Blockly.Msg.PROCEDURES_DEFNORETURN_DO);
    this.setInputsInline(true);
    this.setTooltip('');
  }
};

Blockly.Blocks['lapp_every'] = {
  init: function() {
    //this.setHelpUrl('http://www.example.com/');
    this.setColour(70);
    this.appendValueInput("LOOPTIME")
        .setCheck("Number")
        .setAlign(Blockly.ALIGN_CENTRE)
        .appendField(Blockly.Msg.BBLAMP_EVERY_TITLE);
    this.appendDummyInput()
        .appendField(Blockly.Msg.BBLAMP_EVERY_SECONDS);
    this.appendStatementInput("STACK")
        .appendField(Blockly.Msg.PROCEDURES_DEFNORETURN_DO);
    this.setInputsInline(true);
    this.setTooltip('');
  }
};

Blockly.Blocks['lapp_wait'] = {
  init: function() {
//    this.setHelpUrl('http://www.example.com/');
    this.setColour(20);
    this.appendValueInput("TIME")
        .setCheck("Number")
        .appendField(Blockly.Msg.BBLAMP_WAIT_TITLE);
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown(
                [[Blockly.Msg.BBLAMP_WAIT_SECONDS, "SEC"],
                    [Blockly.Msg.BBLAMP_WAIT_MILLISECONDS, "MILLISEC"]]),
            "UNIT");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};

/******************************************************************************/
Blockly.Blocks['leds_turn_on'] = {
  init: function() {
    //this.setHelpUrl('http://www.example.com/');
    this.setColour(330);
    this.appendValueInput("ID")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(Blockly.Msg.BBLAMP_TURNON_TITLE);
    this.appendValueInput("COLOUR")
        .setCheck("Colour")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(Blockly.Msg.BBLAMP_TURNON_TOCOLOR);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};

Blockly.Blocks['leds_turn_off'] = {
  init: function() {
    //this.setHelpUrl('http://www.example.com/');
    this.setColour(330);
    this.appendValueInput("ID")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(Blockly.Msg.BBLAMP_TURNOFF_TITLE);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};
