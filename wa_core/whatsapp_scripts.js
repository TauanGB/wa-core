/**
 * Scripts JavaScript para automação do WhatsApp Web
 * Centraliza todas as funções JavaScript utilizadas pelo SeleniumDriver
 */

(() => {
  function setText(el, text, { append = false } = {}) {
    el.focus();

    // Limpa o campo (se não for append)
    if (!append) {
      const sel = window.getSelection();
      sel.removeAllRanges();
      const range = document.createRange();
      range.selectNodeContents(el);
      sel.addRange(range);
      document.execCommand('delete');
      el.dispatchEvent(new InputEvent('input', { bubbles: true }));
    }

    // Insere texto de forma compatível com apps baseados em React
    const parts = String(text).split(/\\n/);
    parts.forEach((p, i) => {
        if (p) document.execCommand('insertText', false, p);
        if (i < parts.length - 1) {
            el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter',code: 'Enter',keyCode: 13,which: 13,shiftKey: true,bubbles: true,cancelable: true,composed: true}));
            el.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter',code: 'Enter',keyCode: 13,which: 13,shiftKey: true,bubbles: true,cancelable: true,composed: true}));
            el.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter',code: 'Enter',keyCode: 13,which: 13,shiftKey: true,bubbles: true,cancelable: true,composed: true}));
        }
    });
    console.log('Texto inserido:', text);
    el.dispatchEvent(new InputEvent('input', { bubbles: true }));
  }

  // Exponha uma função global para usar facilmente:
  window.whatsType = function (text, { append = false } = {}) {
    let elemento = document.evaluate(
		'//div[@aria-placeholder and @spellcheck and @aria-activedescendant]', 
		document,
		null,
		XPathResult.FIRST_ORDERED_NODE_TYPE,
		null
	  ).singleNodeValue;

    if (!elemento) {
      console.warn('Não encontrei o campo de mensagem. Abra uma conversa e tente novamente.');
      return false;
    }
    setText(elemento, text, { append });
    // Retorna true se conseguiu inserir o texto, mas não tenta enviar
    return true;
  };

  console.log('Pronto! Use: whatsType("Sua mensagem aqui") - O envio será feito via Selenium');
})();

window.sendToWhatsAppSearch = async function(text = "Seu texto de busca aqui") {
	// Seleciona o primeiro elemento que corresponde ao XPath
	let elemento = document.evaluate(
	  '//div[@id="side"]//div[contains(@class,"lexical-rich-text-input")]//div[@aria-placeholder]', 
	  document,
	  null,
	  XPathResult.FIRST_ORDERED_NODE_TYPE,
	  null
	).singleNodeValue;
	
	const getBox = () => elemento;
  
	// Espera a barra de busca aparecer (SPA)
	const waitForEl = (timeoutMs = 8000) =>
	  new Promise((resolve, reject) => {
		const t0 = performance.now();
		(function loop() {
		  const el = getBox();
		  if (el) return resolve(el);
		  if (performance.now() - t0 > timeoutMs) return reject(new Error("Barra de pesquisa não encontrada."));
		  requestAnimationFrame(loop);
		})();
	  });
  
	const typeText = (el, value) => {
	  el.focus();
  
	  // Limpa de forma "oficial"
	  document.execCommand('selectAll', false, null);
	  document.execCommand('delete', false, null);
  
	  // Tenta inserir de forma compatível com contenteditable/React
	  const ok = document.execCommand('insertText', false, value);
  
	  if (!ok) {
		// Fallback: atualiza DOM e dispara eventos que o Lexical/React costuma ouvir
		el.textContent = value;
		el.dispatchEvent(new InputEvent('beforeinput', { bubbles: true, cancelable: true, inputType: 'insertText', data: value }));
		el.dispatchEvent(new InputEvent('input',       { bubbles: true, cancelable: true, inputType: 'insertText', data: value }));
		el.dispatchEvent(new Event('change', { bubbles: true }));
	  }
  
	  // Alguns handlers reagem a keyup
	  el.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'Unidentified' }));
	};
  
	const el = await waitForEl();
	typeText(el, text);
	return true;
  };
  

// Exemplo de uso (rode isto depois):
// sendToWhatsAppSearch("nome do contato ou termo de busca");
