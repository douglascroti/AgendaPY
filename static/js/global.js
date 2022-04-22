$(document).ready(function () {

    $(".custom-file-input").on("change", function () {
        var fileName = $(this).val().split("\\").pop();
        $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });

    $('.mascaraCEP').mask('99999-999');

    $('.mascaraFone').mask("(99)99999-9999").focusout(function (event) {
        var target, phone, element;
        target = (event.currentTarget) ? event.currentTarget : event.srcElement;
        phone = target.value.replace(/\D/g, '');
        element = $(target);
        element.unmask();
        if (phone.length > 10) {
            element.mask("(99)99999-9999");
        } else {
            element.mask("(99)9999-99999");
        }
    });

    function dispararAlerta(msg, status = 'warning', time = 5000, icon = '') {
        $('.alert').remove();
        $.notify({
            icon: icon,
            message: msg
        }, {
            type: status,
            allow_dismiss: true,
            newest_on_top: true,
            showProgressbar: false,
            placement: {
                from: "top",
                align: "center"
            },
            z_index: 1031,
            delay: time,
            timer: 200,
            animate: {
                enter: 'animated fadeInDown',
                exit: 'animated fadeOutUp'
            }
        });
    }

    if ($('#exibirMensagem').val() != "" && $('#exibirMensagem').val() != undefined) {
        let msg = $('#exibirMensagem').val();
        let status = 'warning';
        $('#exibirMensagem').val("");

        dispararAlerta(msg, status);
    }

    /****************************** CONTATOS *********************************/
    $(document).on('click', '.alterarSenhaUsuario', function () {
        bootbox.prompt({
            title: "Informe a nova senha",
            inputType: 'password',
            centerVertical: true,
            callback: function (result) {
                if (result)
                {
                    let senha = result;
                    $.ajax({
                        url: 'http://127.0.0.1:5000/usuario/alteraSenha',
                        type: 'POST',
                        contentType: "application/json",
                        dataType: 'JSON',
                        data: JSON.stringify({senha: senha})
                    }).done(function (data) {

                        console.log(data['mensagem'])
                        dispararAlerta(data['mensagem']);

                    }).fail(function () {
                        dispararAlerta('Falha na Chamada Ajax');
                    });
                }

            }
        });
    });
    
    $(document).on('click', '.editarUsuario', function () {

        $('form[name=salvarAcessoAdmin] input[name=codigo]').val('');
        $('form[name=salvarAcessoAdmin] input[name=login]').val('');
        $('form[name=salvarAcessoAdmin] input[name=senha]').val('');

        let codigo = $(this).data('codigo');
        let login = $(this).data('login');

        $('form[name=salvarAcessoAdmin] input[name=codigo]').val(codigo);
        $('form[name=salvarAcessoAdmin] input[name=login]').val(login);
        $('form[name=salvarAcessoAdmin] input[name=senha]').focus();
    });

    $(document).on('dblclick', '.detalheContato-dbClick', function () 
    {
        let codigo = $(this).data('codigo');
        abreModalDetalhe(codigo);
    });

    $(document).on('click', '.detalheContato', function () 
    {
        let codigo = $(this).data('codigo');
        abreModalDetalhe(codigo);
    });

    function abreModalDetalhe(codigo)
    {
        limpaModalDetalhe();
        $.ajax({
            url: 'http://127.0.0.1:5000/index/detalhe',
            type: 'POST',
            contentType: "application/json",
            dataType: 'JSON',
            data: JSON.stringify({codigo: codigo})
        }).done(function (data) {

            if (data.length > 0)
            {
                let dados = data[0];
                $('#modal-detalheContato-label').text('Detalhes do Contato: '+dados[1]);
                $('#md-lb-codigo').text(dados[0]);
                $('#md-lb-nome').text(dados[1]);
                $('#md-lb-email').text(dados[2]);
                $('#md-lb-fone').text(dados[3]);
                $('#md-lb-cep').text(dados[4]);
                $('#md-lb-cidade').text(dados[5]);
                $('#md-lb-bairro').text(dados[7]);
                $('#md-lb-endereco').text(dados[8]);
                $('#md-lb-avatar').attr('src', dados[9]+dados[10]);

                $('#modal-detalheContato').modal('show');
            } else {
                dispararAlerta('Nenhum resultado encontrado');    
            }
        }).fail(function () {
            dispararAlerta('Falha na Chamada Ajax');
        });
    }

    $(document).on('click', '.api-cep-json', function () {
        let cep = $('#cep').val();
        if (cep != '')
        {
            $('#cidade').val('');
            $('#bairro').val('');
            $('#endereco').val('');
            $('#complemento').val('');

            $.ajax({
                url: 'http://127.0.0.1:5000/contato/api_json',
                type: 'POST',
                contentType: "application/json",
                dataType: 'JSON',
                data: JSON.stringify({cep: cep})
            }).done(function (data) {
                
                if (!data['error'])
                {
                    let dados = data['data'];
                    $('#cidade').val(dados['localidade']+' / '+dados['uf']);
                    $('#bairro').val(dados['bairro']);
                    $('#endereco').val(dados['logradouro']);
                    $('#complemento').val(dados['complemento']);                
                }
            }).fail(function () {
                dispararAlerta('Falha na Chamada Ajax');
            });
        }            
    });

    $(document).on('click', '.api-cep-xml', function () {
        let cep = $('#cep').val();
        if (cep != '')
        {
            $('#cidade').val('');
            $('#bairro').val('');
            $('#endereco').val('');
            $('#complemento').val('');
            
            $.ajax({
                url: 'http://127.0.0.1:5000/contato/api_xml',
                type: 'POST',
                contentType: "application/json",
                dataType: 'JSON',
                data: JSON.stringify({cep: cep})
            }).done(function (data) {

                if (!data['error'])
                {
                    let dados = data['data'];
                    $('#cidade').val(dados['localidade']+' / '+dados['uf']);
                    $('#bairro').val(dados['bairro']);
                    $('#endereco').val(dados['logradouro']);
                    $('#complemento').val(dados['complemento']);                
                }
    
            }).fail(function () {
                dispararAlerta('Falha na Chamada Ajax');
            });
        }            
    });

    $(document).on('blur', '#txt-filtroContato', function (e) {
        n_href = '/index';
        if ($(this).val() != '') 
        {
            n_href = n_href+'?parametro='+$(this).val();    
        }
        $('#btn-pesquisaContato').attr("href", n_href);
    });

    function limpaModalDetalhe()
    {
        $('#modal-detalheContato-label').text('');
        $('#md-lb-codigo').text('');
        $('#md-lb-nome').text('');
        $('#md-lb-email').text('');
        $('#md-lb-fone').text('');
        $('#md-lb-cep').text('');
        $('#md-lb-cidade').text('');
        $('#md-lb-bairro').text('');
        $('#md-lb-endereco').text('');
        $('#md-lb-avatar').attr('src', '');
    }

    $('#modal-detalheContato').on('hidden.bs.modal', function() 
    {
        limpaModalDetalhe();
    });

});
