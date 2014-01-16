/**
 * Visual Blocks Language
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
 * @fileoverview Generating Python for procedure blocks.
 * @author enavarro222@gmail.com (Emmanuel Navarro)
 */
'use strict';

goog.provide('Blockly.Python.lapp');

goog.require('Blockly.Python');

Blockly.Python.LAMPAPP_IMPORT = 'from lampapp import LampApp';
Blockly.Python.LAMPAPP_DEF = 'app = LampApp()';

/**
 * 
 */
Blockly.Python._lapp_needed = function(){
  Blockly.Python.definitions_['import_lampapp'] = Blockly.Python.LAMPAPP_IMPORT;
  Blockly.Python.definitions_['def_lampapp'] = Blockly.Python.LAMPAPP_DEF;
}

// Define a lapp "setup" procedure.
Blockly.Python['lapp_setup'] = function(block) {
  Blockly.Python._lapp_needed();
  // First, add a 'global' statement for every variable that is assigned.
  var globals = Blockly.Variables.allVariables(block);
  for (var i = globals.length - 1; i >= 0; i--) {
    var varName = globals[i];
  }
  globals = globals.length ? '    global ' + globals.join(', ') + '\n' : '';
  // register the name of the procedure and (and rename it if needed)
  var funcName = Blockly.Python.variableDB_.getName('setup', Blockly.Generator.NAME_TYPE)
  var decorator = '@app.setup()\n';
  // code of the procedure
  var branch = Blockly.Python.statementToCode(block, 'STACK');
  if (Blockly.Python.INFINITE_LOOP_TRAP) {
    branch = Blockly.Python.INFINITE_LOOP_TRAP.replace(/%1/g,
        '"' + block.id + '"') + branch;
  }
  if (!branch) { // if no code
    branch = '    pass';
  }
  
  var code = decorator + 'def ' + funcName + '():\n' +
      globals + branch;
  code = Blockly.Python.scrub_(block, code);
  Blockly.Python.definitions_[funcName] = code;
  return null;
};

// Define a lapp "every" procedure.
Blockly.Python['lapp_every'] = function(block) {
  Blockly.Python._lapp_needed();
  
  // First, add a 'global' statement for every variable that is assigned.
  var globals = Blockly.Variables.allVariables(block);
  for (var i = globals.length - 1; i >= 0; i--) {
    var varName = globals[i];
  }
  globals = globals.length ? '    global ' + globals.join(', ') + '\n' : '';
  // register the name of the procedure and (and rename it if needed)
  var funcName = Blockly.Python.variableDB_.getDistinctName('every', Blockly.Generator.NAME_TYPE)
  // looptime value
  var value_looptime = Blockly.Python.valueToCode(block, 'LOOPTIME',
    Blockly.Python.ORDER_ATOMIC);
  var decorator = '@app.every('+value_looptime+')\n';
  // code of the procedure
  var branch = Blockly.Python.statementToCode(block, 'STACK');
  if (Blockly.Python.INFINITE_LOOP_TRAP) {
    branch = Blockly.Python.INFINITE_LOOP_TRAP.replace(/%1/g,
        '"' + block.id + '"') + branch;
  }
  if (!branch) { // if no code
    branch = '    pass';
  }
  
  var code = decorator + 'def ' + funcName + '():\n' +
      globals + branch;
  code = Blockly.Python.scrub_(block, code);
  Blockly.Python.definitions_[funcName] = code;
  return null;
};


Blockly.Python['lapp_wait'] = function(block) {
  Blockly.Python._lapp_needed();

  var value_time = Blockly.Python.valueToCode(block, 'TIME', Blockly.Python.ORDER_ATOMIC) || '0';
  var dropdown_unit = block.getFieldValue('UNIT');
  // TODO: Assemble Python into code variable.
  if(dropdown_unit == 'MILLISEC'){
    // TODO: use blockly operation priorit to prevent unuseful ( )
    value_time = '(' + value_time + ') / 1000.';
  }
  var code = 'app.wait('+value_time+')\n';
  return code;
};

/******************************************************************************/

Blockly.Python['leds_turn_on'] = function(block) {
  Blockly.Python._lapp_needed();

  var value_id = Blockly.Python.valueToCode(block, 'ID', Blockly.Python.ORDER_ATOMIC) || 'None';
  var value_colour = Blockly.Python.valueToCode(block, 'COLOUR', Blockly.Python.ORDER_ATOMIC) || 'None';
  var code = 'app.lamp.turn_on('+value_id+', '+value_colour+')\n';
  return code;
};

Blockly.Python['leds_turn_off'] = function(block) {
  Blockly.Python._lapp_needed();

  var value_id = Blockly.Python.valueToCode(block, 'ID', Blockly.Python.ORDER_ATOMIC) || 'None';
  var code = 'app.lamp.turn_off('+value_id+')\n';
  return code;
};
